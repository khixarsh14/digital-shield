import base64
import json
from unittest.mock import Mock
from urllib.error import HTTPError, URLError

import pytest

from backend.tools import vision_tool
from backend.utils import media_upload


PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")
# Container signatures exercise upload routing; Gemini decoding is mocked.
MP4 = (24).to_bytes(4, "big") + b"ftypisom" + b"\0" * 4 + b"isommp42"
MOV = (20).to_bytes(4, "big") + b"ftypqt  " + b"\0" * 4 + b"qt  "


def evidence(video=False):
    return {
        "summary": "A payment registration claim appears.",
        "visible_text": "Congratulations! You are eligible for a BISP payment. Register before midnight: https://bisp-payment-example.xyz",
        "spoken_text": "Government has announced a new Rs. 25,000 payment." if video else "",
        "urls": ["https://bisp-payment-example.xyz"],
        "claims": ["Users are eligible for a BISP payment."],
        "organizations": ["BISP"], "signals": ["payment_claim", "urgency"],
        "observations": ["Registration is requested through a displayed link."],
        "timestamps": [{"time": "00:08", "observation": "A registration URL appears."}] if video else [],
        "confidence": "medium", "manipulation_assessment": "unable_to_determine",
    }


def gemini_result(data):
    return {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": json.dumps(data)}]}}]}


@pytest.fixture
def gemini(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-key")
    generate = Mock(return_value=gemini_result(evidence()))
    monkeypatch.setattr(vision_tool, "_generate", generate)
    return generate


@pytest.mark.parametrize("name,mime,data", [
    ("demo.png", "image/png", PNG),
    ("demo.jpg", "image/jpeg", b"\xff\xd8\xff\xe0test"),
    ("demo.jpeg", "image/jpeg", b"\xff\xd8\xff\xe0test"),
    ("demo.webp", "image/webp", b"RIFF\x10\0\0\0WEBPtest"),
])
def test_image_upload_evidence(client, gemini, name, mime, data):
    response = client.post("/analyze-media", files={"file": (name, data, mime)})
    assert response.status_code == 200
    result = response.json()
    assert result["media_type"] == "image" and result["status"] == "analyzed"
    assert result["evidence"] == evidence()
    gemini.assert_called_once()
    assert gemini.call_args.args[:2] == (data, mime)


def test_otp_screenshot_evidence(client, gemini):
    observed = evidence()
    observed.update(visible_text="Your bank account will be blocked. Send your OTP immediately.",
                    claims=[], urls=[], organizations=[], signals=["account_threat", "otp_request", "urgency"])
    gemini.return_value = gemini_result(observed)
    response = client.post("/analyze-media", files={"file": ("otp.png", PNG, "image/png")})
    assert response.json()["evidence"]["signals"] == observed["signals"]


@pytest.mark.parametrize("name,mime,data", [
    ("demo.mp4", "video/mp4", MP4), ("demo.mov", "video/quicktime", MOV),
    ("demo.webm", "video/webm", b"\x1a\x45\xdf\xa3webmtest"),
])
def test_video_upload_evidence(client, gemini, name, mime, data):
    gemini.return_value = gemini_result(evidence(video=True))
    response = client.post("/analyze-media", files={"file": (name, data, mime)})
    assert response.status_code == 200
    result = response.json()
    assert result["media_type"] == "video" and result["status"] == "analyzed"
    assert result["evidence"] == evidence(video=True)


@pytest.mark.parametrize("name,mime,data", [
    ("demo.gif", "image/gif", b"GIF89a"), ("demo.avi", "video/x-msvideo", b"RIFF"),
    ("demo.png", "image/jpeg", PNG), ("demo.png", "image/png", b"not an image"),
    ("demo.mp4", "video/mp4", PNG),
])
def test_unsupported_and_mismatched_uploads(client, gemini, name, mime, data):
    response = client.post("/analyze-media", files={"file": (name, data, mime)})
    assert response.status_code == 415
    assert isinstance(response.json()["detail"], str)
    gemini.assert_not_called()


@pytest.mark.parametrize("name,mime,header", [("big.png", "image/png", PNG), ("big.mp4", "video/mp4", MP4)])
@pytest.mark.parametrize("excess", [1, 65537])
def test_oversized_uploads(client, gemini, monkeypatch, name, mime, header, excess):
    monkeypatch.setattr(media_upload, "max_upload_bytes", lambda: 1024)
    data = header + b"x" * (1024 + excess - len(header))
    response = client.post("/analyze-media", files={"file": (name, data, mime)})
    assert response.status_code == 413
    gemini.assert_not_called()


def test_empty_and_missing_upload(client, gemini):
    assert client.post("/analyze-media", files={"file": ("empty.png", b"", "image/png")}).status_code == 422
    assert client.post("/analyze-media").status_code == 422
    gemini.assert_not_called()


@pytest.mark.parametrize("video", [False, True])
def test_missing_key(video, monkeypatch):
    generate = Mock()
    monkeypatch.setattr(vision_tool, "_generate", generate)
    tool = vision_tool.analyze_video if video else vision_tool.analyze_image
    result = tool(MP4 if video else PNG, "video/mp4" if video else "image/png")
    assert result.status == "unavailable" and result.evidence is None
    generate.assert_not_called()


@pytest.mark.parametrize("error", [URLError("secret"), TimeoutError("secret"),
                                   HTTPError("secret", 429, "secret", {}, None),
                                   HTTPError("secret", 500, "secret", {}, None)])
@pytest.mark.parametrize("video", [False, True])
def test_provider_failures(gemini, error, video):
    gemini.side_effect = error
    tool = vision_tool.analyze_video if video else vision_tool.analyze_image
    result = tool(MP4 if video else PNG, "video/mp4" if video else "image/png")
    assert result.status == "unavailable" and result.evidence is None
    assert "secret" not in result.model_dump_json()


@pytest.mark.parametrize("response", [
    {}, {"candidates": []}, {"candidates": [{"finishReason": "SAFETY"}]},
    gemini_result({"summary": "missing fields"}),
    {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "not JSON"}]}}]},
])
def test_malformed_gemini_response(gemini, response):
    gemini.return_value = response
    result = vision_tool.analyze_image(PNG, "image/png")
    assert result.status == "invalid_response" and result.evidence is None


def test_invalid_video_timestamp(gemini):
    observed = evidence(video=True)
    observed["timestamps"][0]["time"] = "sometime"
    gemini.return_value = gemini_result(observed)
    assert vision_tool.analyze_video(MP4, "video/mp4").status == "invalid_response"


def test_gemini_request_contract(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-key")
    from unittest.mock import MagicMock
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = json.dumps(gemini_result(evidence())).encode()
    transport = Mock(return_value=response)
    monkeypatch.setattr(vision_tool, "urlopen", transport)
    assert vision_tool.analyze_image(PNG, "image/png").status == "analyzed"
    request = transport.call_args.args[0]
    body = json.loads(request.data)
    assert request.full_url.endswith("gemini-2.5-flash:generateContent")
    assert body["generationConfig"]["responseMimeType"] == "application/json"
    inline = body["contents"][0]["parts"][0]["inlineData"]
    assert base64.b64decode(inline["data"]) == PNG
    assert inline["mimeType"] == "image/png"
    assert transport.call_args.kwargs["timeout"] == 60
