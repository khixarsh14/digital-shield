from unittest.mock import Mock, call

import pytest

from backend.agent import verifier
from backend.models.media import MediaAnalysis, MediaEvidence
from backend.models.schemas import VerifyRequest
from backend.tools.claim_verifier import ClaimSource, ClaimVerification


CLAIM = "BISP has launched a new payment scheme."


def claim_result(status, trusted=True):
    return ClaimVerification(claim=CLAIM, status=status, explanation="Mock evidence",
        evidence=[ClaimSource(title="Official announcement", url="https://bisp.gov.pk/notice",
                              snippet=CLAIM, trusted=trusted, source_kind="official" if trusted else "other")])


def media_result(kind="image", **changes):
    data = dict(summary="Extracted evidence", visible_text="Send your OTP immediately.", spoken_text="",
                urls=["https://bit.ly/demo"], claims=[CLAIM], organizations=["BISP"], signals=[],
                observations=[], timestamps=[], confidence="medium", manipulation_assessment="no_clear_manipulation_evidence")
    data.update(changes)
    return MediaAnalysis(media_type=kind, status="analyzed", evidence=MediaEvidence(**data), explanation="Test")


def test_plain_text_skips_external_tools(monkeypatch):
    claim = Mock()
    image = Mock()
    video = Mock()
    url = Mock()
    monkeypatch.setattr(verifier, "verify_claim", claim)
    monkeypatch.setattr(verifier, "analyze_image", image)
    monkeypatch.setattr(verifier, "analyze_video", video)
    monkeypatch.setattr(verifier, "check_url", url)
    assert verifier.verify_content(VerifyRequest(content="Send me the assignment PDF.")).status == "green"
    for tool in [claim, image, video, url]:
        tool.assert_not_called()


@pytest.mark.parametrize("claim_status,expected", [
    ("confirmed", "green"), ("contradicted", "red"),
    ("conflicting", "yellow"), ("insufficient_evidence", "yellow"),
])
def test_claim_risk_and_sources(monkeypatch, claim_status, expected):
    tool = Mock(return_value=claim_result(claim_status))
    monkeypatch.setattr(verifier, "verify_claim", tool)
    response = verifier.verify_content(VerifyRequest(content=CLAIM))
    tool.assert_called_once_with(CLAIM)
    assert response.status == expected
    assert str(response.sources[0].url) == "https://bisp.gov.pk/notice"
    if claim_status == "insufficient_evidence":
        assert any("does not mean it is false" in reason for reason in response.reasons)


def test_untrusted_sources_do_not_support_red_or_confirmation(monkeypatch):
    monkeypatch.setattr(verifier, "verify_claim", Mock(return_value=claim_result("contradicted", trusted=False)))
    response = verifier.verify_content(VerifyRequest(content=CLAIM))
    assert response.status == "yellow" and response.sources == []


def test_confirmed_claim_cannot_override_credential_risk(monkeypatch):
    monkeypatch.setattr(verifier, "verify_claim", Mock(return_value=claim_result("confirmed")))
    response = verifier.verify_content(VerifyRequest(content=CLAIM + " Send your OTP immediately."))
    assert response.status == "red"


def test_missing_claim_key_produces_uncertainty(client):
    response = client.post("/verify", json={"content": CLAIM})
    assert response.status_code == 200
    assert response.json()["status"] == "yellow"
    assert response.json()["sources"] == []


@pytest.mark.parametrize("kind,mime", [("image", "image/png"), ("video", "video/mp4")])
def test_media_selects_one_tool_and_reuses_extracted_evidence(monkeypatch, kind, mime):
    extracted = media_result(kind, visible_text=CLAIM + "\nSend your OTP immediately.\nhttps://bit.ly/demo")
    image = Mock(return_value=extracted)
    video = Mock(return_value=extracted)
    scam = Mock(wraps=verifier.check_scam)
    url = Mock(wraps=verifier.check_url)
    claim = Mock(return_value=claim_result("confirmed"))
    for name, tool in [("analyze_image", image), ("analyze_video", video), ("check_scam", scam),
                       ("check_url", url), ("verify_claim", claim)]:
        monkeypatch.setattr(verifier, name, tool)
    response = verifier.verify_media(b"test-media", mime, "ur")
    (image if kind == "image" else video).assert_called_once_with(b"test-media", mime)
    (video if kind == "image" else image).assert_not_called()
    scam.assert_called_once()
    assert "Send your OTP" in scam.call_args.args[0]
    url.assert_called_once_with("https://bit.ly/demo")
    claim.assert_called_once_with(CLAIM)
    assert response.status == "red" and response.language == "ur"
    assert len(response.sources) == 1


@pytest.mark.parametrize("status", ["unavailable", "invalid_response"])
def test_failed_media_is_yellow_without_downstream_calls(monkeypatch, status):
    monkeypatch.setattr(verifier, "analyze_image", Mock(return_value=MediaAnalysis(
        media_type="image", status=status, explanation="Unavailable")))
    scam, url, claim = Mock(), Mock(), Mock()
    monkeypatch.setattr(verifier, "check_scam", scam)
    monkeypatch.setattr(verifier, "check_url", url)
    monkeypatch.setattr(verifier, "verify_claim", claim)
    response = verifier.verify_media(b"data", "image/png")
    assert response.status == "yellow" and response.sources == []
    for tool in [scam, url, claim]:
        tool.assert_not_called()


def test_visual_suspicion_alone_is_not_red(monkeypatch):
    monkeypatch.setattr(verifier, "analyze_image", Mock(return_value=media_result(
        visible_text="A landscape.", urls=[], claims=[], signals=["possible_manipulation"],
        manipulation_assessment="possible_manipulation")))
    assert verifier.verify_media(b"data", "image/png").status == "yellow"


def test_multiple_claims_and_sources_are_deduplicated(monkeypatch):
    other = "HEC has announced a new policy."
    tool = Mock(side_effect=lambda text: claim_result("confirmed").model_copy(update={"claim": text}))
    monkeypatch.setattr(verifier, "verify_claim", tool)
    response = verifier.verify_content(VerifyRequest(content=CLAIM + " " + CLAIM + " " + other))
    assert tool.call_args_list == [call(CLAIM), call(other)]
    assert len(response.sources) == 1


def test_upload_opt_in_preserves_default_api(client, monkeypatch):
    # Signature fixture: Gemini is mocked, not the multipart parser.
    data = b"\x89PNG\r\n\x1a\ntest"
    observed = media_result(visible_text="Can you send the assignment PDF?", urls=[], claims=[])
    monkeypatch.setattr(verifier, "analyze_image", Mock(return_value=observed))
    response = client.post("/analyze-media?verify=true&language=ur", files={"file": ("test.png", data, "image/png")})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "yellow" and body["language"] == "ur"
    assert "sources" in body and "evidence" not in body
    assert client.post("/analyze-media?verify=true&language=fr", files={"file": ("test.png", data, "image/png")}).status_code == 422
