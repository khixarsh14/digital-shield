"""Conservative English claim candidates; detection is not verification."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ClaimCandidate:
    has_claim: bool
    claim: str | None = None


def sentences(content: str) -> list[str]:
    # Keep Rs. amounts together rather than splitting the payment claim.
    protected = re.sub(r"\bRs\.(?=\s*\d)", "Rs\u0000", content, flags=re.I)
    return [part.replace("\u0000", ".").strip() for part in
            re.split(r"(?<=[.!?])\s+|[\r\n]+", protected) if part.strip()]


_SUBJECT = r"(?:HEC|BISP|NADRA|HBL|Easypaisa|JazzCash|(?:the\s+)?(?:government|bank|university|ministry))"
_STATEMENT = re.compile(
    r"^" + _SUBJECT + r"\s+(?:(?:has|have|had)\s+)?"
    r"(?:announced|launched|made|approved|introduced|extended|changed|decided|"
    r"will\s+(?:close|remain|provide|pay|launch|change)|is\s+(?:closed|offering))\b",
    re.I,
)


def detect_claim(content: str) -> ClaimCandidate:
    """Return the first institutional statement, never an imperative/question."""
    for sentence in sentences(content):
        if "?" not in sentence and _STATEMENT.search(sentence):
            return ClaimCandidate(True, sentence)
    return ClaimCandidate(False)
