"""Deterministic English scam indicators, without network or model calls."""

from dataclasses import dataclass
import re
from typing import Literal
import unicodedata


Signal = Literal[
    "money_request", "urgency", "otp_request", "credential_request",
    "reward", "threat", "suspicious_action", "impersonation",
]


@dataclass(frozen=True)
class ScamEvidence:
    signals: tuple[Signal, ...]
    reasons: tuple[str, ...]
    score: int
    has_arabic_script: bool


_REQUEST = r"\b(?:send|share|provide|give|enter|submit|disclose|tell)\b"
_GAP = r"(?:[\s,:]+[\w'-]+){0,5}[\s,:]+"
_RULES: tuple[tuple[Signal, str, str], ...] = (
    ("money_request",
     r"\b(?:send|pay|transfer|deposit|wire)\b" + _GAP
     + r"(?:rs\.?|pkr|usd|money|payment|fee|deposit|cash|rupees|dollars)\b"
     + r"|\b(?:send|pay|transfer|deposit|wire)\s+[$£€]?\s*\d",
     "The message asks for money or a payment."),
    ("urgency",
     r"\b(?:act now|immediately|urgently|urgent action|last chance|limited time)\b"
     + r"|\b(?:send|pay|reply|respond|act|confirm|click|verify|submit|register|login)\b"
     + _GAP + r"(?:today|now|asap|before midnight|within \d+ (?:minutes|hours))\b",
     "The message pressures you to act quickly."),
    ("otp_request", _REQUEST + _GAP + r"(?:otp|one[ -]time (?:password|code)|verification code)\b",
     "The message asks for an OTP or verification code."),
    ("credential_request", _REQUEST + _GAP + r"(?:pin|password|passcode|login credentials)\b",
     "The message asks for a PIN, password, or login credentials."),
    ("reward",
     r"\byou(?: have|'ve)?\s+(?:won|been selected (?:as|for) (?:a |the )?(?:winner|prize|reward))\b"
     + r"|\b(?:claim|receive|collect)\s+(?:your |a |the )?(?:prize|reward|winnings|lottery)\b",
     "The message promises a prize or reward."),
    ("threat",
     r"\b(?:account|card|access)\s+(?:(?:will|would) be|is|has been)\s+(?:blocked|suspended|closed|disabled)\b"
     + r"|\b(?:face arrest|legal action will be taken)\b",
     "The message threatens account restrictions or legal consequences."),
    ("suspicious_action",
     r"\b(?:click|open|visit|follow)\s+(?:on )?(?:this|the|our|following)\s+link\b"
     + r"|\b(?:install|download)\s+(?:this|our|the)\s+(?:remote access|support)\s+(?:app|software)\b",
     "The message asks you to follow a link or install remote-access software."),
    ("impersonation",
     r"\b(?:we are|i am|this is|calling)\s+(?:from )?(?:your|the)\s+(?:bank|bank's|government|tax office|police)\b"
     + r"|\b(?:official|authorized)\s+(?:bank|government|support)\s+(?:agent|representative|team)\b",
     "The sender claims to represent an official organization; that claim is unverified."),
)


def _positive_match(pattern: str, clause: str) -> bool:
    for match in re.finditer(pattern, clause):
        prefix = clause[:match.start()]
        # Ignore nearby negated instructions, without suppressing later clauses.
        if re.search(r"\b(?:never|not|don't|dont|avoid)\b(?:[\s]+[\w'-]+){0,3}\s*$", prefix):
            continue
        if re.search(r"\b(?:not|never)\b", match.group()):
            continue
        return True
    return False


def check_scam(content: str) -> ScamEvidence:
    """Return each matched signal once; score counts signals, not probability."""
    normalized = unicodedata.normalize("NFKC", content).casefold().replace("’", "'")
    # Keep decimal amounts and Rs. together while isolating instructions.
    normalized = re.sub(r"\brs\.\s*", "rs ", normalized)
    clauses = re.split(r"[!?;\n]+|\.(?!\d)|\bbut\b", normalized)
    signals: list[Signal] = []
    reasons: list[str] = []
    for signal, pattern, reason in _RULES:
        if any(_positive_match(pattern, clause) for clause in clauses):
            signals.append(signal)
            reasons.append(reason)
    return ScamEvidence(
        signals=tuple(signals), reasons=tuple(reasons), score=len(signals),
        has_arabic_script=bool(re.search(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]", normalized)),
    )
