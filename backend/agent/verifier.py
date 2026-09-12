"""Deterministic verification orchestration using local evidence tools."""

from collections.abc import Sequence

from backend.models.schemas import Language, Source, VerifyRequest, VerifyResponse
from backend.models.media import MediaAnalysis
from backend.tools.scam_checker import ScamEvidence, check_scam
from backend.tools.url_checker import check_url, extract_urls
from backend.tools.claim_detector import detect_claim, sentences
from backend.tools.claim_verifier import verify_claim
from backend.tools.vision_tool import analyze_image, analyze_video


def verify_content(request: VerifyRequest) -> VerifyResponse:
    return _verify(request.content, request.language)


def verify_media(data: bytes, mime: str, language: Language = "en") -> VerifyResponse:
    """Select one media tool, then reuse text, URL, and claim evidence collectors."""
    if mime.startswith("image/"):
        media = analyze_image(data, mime)
    elif mime.startswith("video/"):
        media = analyze_video(data, mime)
    else:
        return VerifyResponse(status="yellow", label="Verify First",
                              summary="This media type could not be checked.", language=language)
    extracted = media.evidence if media.status == "analyzed" else None
    content = "\n".join([extracted.visible_text, extracted.spoken_text]) if extracted else ""
    return _verify(content, language, extracted.urls if extracted else (),
                   extracted.claims if extracted else (), media)


def _verify(content: str, language: Language, extra_urls: Sequence[str] = (), extra_claims: Sequence[str] = (),
            media: MediaAnalysis | None = None) -> VerifyResponse:
    evidence = check_scam(content) if content.strip() else ScamEvidence((), (), 0, False)
    urls = list(dict.fromkeys([*extract_urls(content), *extra_urls]))
    url_evidence = [check_url(url) for url in urls if url.strip()]
    claims = {}
    for sentence in sentences(content):
        candidate = detect_claim(sentence)
        if candidate.has_claim and candidate.claim:
            claims.setdefault(" ".join(candidate.claim.casefold().split()).rstrip(".!"), candidate.claim)
    for claim in extra_claims:
        if claim.strip():
            claims.setdefault(" ".join(claim.casefold().split()).rstrip(".!"), claim.strip())
    claim_evidence = [verify_claim(claim) for claim in claims.values()]
    sources = {}
    claim_reasons = []
    uncertain_claim = False
    contradicted = False
    for item in claim_evidence:
        for source in item.evidence:
            if source.trusted:
                sources.setdefault(str(source.url), Source(label=source.title, url=source.url))
        reliable = any(source.trusted and source.source_kind == "official" for source in item.evidence)
        if item.status == "contradicted" and reliable:
            contradicted = True
            claim_reasons.append(f'Official evidence contradicts the claim: "{item.claim}"')
        elif item.status == "confirmed" and reliable:
            claim_reasons.append(f'Official search evidence supports the claim: "{item.claim}"; this does not establish overall safety.')
        elif item.status == "conflicting" and reliable:
            uncertain_claim = True
            claim_reasons.append(f'Reliable sources disagree about the claim: "{item.claim}"')
        else:
            uncertain_claim = True
            claim_reasons.append(f'The claim could not be verified: "{item.claim}". This does not mean it is false.')
    media_uncertain = media is not None and (
        media.status != "analyzed" or media.evidence is None or
        media.evidence.confidence == "low" or
        media.evidence.manipulation_assessment != "no_clear_manipulation_evidence" or
        bool(media.evidence.signals) or not (content.strip() or urls or claims)
    )
    suspicious_urls = [item for item in url_evidence if item.signals]
    signals = set(evidence.signals)
    high_risk = bool(signals & {"otp_request", "credential_request"}) or (
        "money_request" in signals and bool(signals & {"urgency", "reward", "threat"})
    )
    strong_url_signals = {"brand_mismatch", "embedded_credentials", "ip_address", "suspicious_keywords"}
    high_risk = high_risk or any(
        len(set(item.signals) & strong_url_signals) >= 2 for item in suspicious_urls
    ) or bool(suspicious_urls and signals & {
        "urgency", "money_request", "reward", "threat", "suspicious_action",
    })
    high_risk = high_risk or contradicted
    reasons = list(dict.fromkeys([
        *evidence.reasons,
        *(reason for item in url_evidence for reason in item.reasons),
        *claim_reasons,
    ]))
    if media is not None:
        reasons.append("Media observations are model-extracted evidence, not proof of authenticity.")
        if media_uncertain:
            reasons.append("Media analysis is incomplete or contains uncertain cues; verify the original source.")
        if media.status == "analyzed" and media.evidence:
            reasons.extend("Media observation: " + item for item in media.evidence.observations)
    reasons = list(dict.fromkeys(reasons))
    actions = ["Verify the sender through an official channel before taking action."]
    if high_risk:
        status, label = "red", "High Risk"
        summary = "This message shows strong scam indicators."
        if signals & {"otp_request", "credential_request"}:
            actions.insert(0, "Do not share your OTP, PIN, or password.")
        if "money_request" in signals:
            actions.insert(0, "Do not send money.")
    elif signals or suspicious_urls or uncertain_claim or media_uncertain:
        status, label = "yellow", "Verify First"
        summary = "This content needs further verification." if uncertain_claim or media_uncertain else "This message contains some suspicious signs."
    elif language == "ur" or evidence.has_arabic_script:
        status, label = "yellow", "Verify First"
        summary = "Only English scam patterns are supported so far; this content could not be fully checked."
    else:
        status, label = "green", "Looks Safe"
        summary = "No strong English text or local URL warning signs were found. This does not guarantee the message is safe."
        actions = ["Stay cautious if the sender is unfamiliar."]
    if "suspicious_action" in signals:
        actions.append("Avoid the requested link or software until you verify the sender.")
    if suspicious_urls:
        actions.extend([
            "Do not open the suspicious link; visit the official website directly.",
            "Do not enter passwords, OTPs, or personal information through the link.",
        ])
    if uncertain_claim or contradicted:
        actions.append("Check the original official announcement before acting on or sharing the claim.")
    return VerifyResponse(
        status=status,
        label=label,
        summary=summary,
        reasons=reasons,
        actions=actions,
        sources=list(sources.values()),
        language=language,
    )
