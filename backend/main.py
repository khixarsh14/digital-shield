import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.models.schemas import HealthResponse, VerifyRequest, VerifyResponse
from backend.tools.scam_checker import check_scam
from backend.tools.url_checker import check_url, extract_urls


app = FastAPI(title="Digital Shield", version="0.1.0")

frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in frontend_origins.split(",") if origin.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.post("/verify", response_model=VerifyResponse)
async def verify(request: VerifyRequest) -> VerifyResponse:
    """Combine local text and URL evidence without agent orchestration."""
    evidence = check_scam(request.content)
    url_evidence = [check_url(url) for url in extract_urls(request.content)]
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
    reasons = list(dict.fromkeys([
        *evidence.reasons,
        *(reason for item in url_evidence for reason in item.reasons),
    ]))
    actions = ["Verify the sender through an official channel before taking action."]
    if high_risk:
        status, label = "red", "High Risk"
        summary = "This message shows strong scam indicators."
        if signals & {"otp_request", "credential_request"}:
            actions.insert(0, "Do not share your OTP, PIN, or password.")
        if "money_request" in signals:
            actions.insert(0, "Do not send money.")
    elif signals or suspicious_urls:
        status, label = "yellow", "Verify First"
        summary = "This message contains some suspicious signs."
    elif evidence.has_arabic_script:
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
    return VerifyResponse(
        status=status,
        label=label,
        summary=summary,
        reasons=reasons,
        actions=actions,
        language=request.language,
    )
