"""Independent Tavily evidence collection; not connected to the API agent."""

import json
from http.client import HTTPException
import os
import re
from typing import Literal
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from pydantic import BaseModel, Field, HttpUrl, ValidationError

from backend.tools.claim_detector import sentences
from backend.tools.url_checker import OFFICIAL_DOMAINS


ClaimStatus = Literal["confirmed", "contradicted", "conflicting", "insufficient_evidence"]
SourceKind = Literal["official", "news", "other"]


class ClaimSource(BaseModel):
    title: str
    url: HttpUrl
    snippet: str
    trusted: bool
    source_kind: SourceKind


class ClaimVerification(BaseModel):
    claim: str
    status: ClaimStatus = "insufficient_evidence"
    evidence: list[ClaimSource] = Field(default_factory=list)
    explanation: str


_NEWS_DOMAINS = {"dawn.com", "reuters.com", "bbc.com"}
_MAX_RESPONSE_BYTES = 1_000_000


def _source_kind(url: str) -> SourceKind:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.username is not None or parsed.password is not None or parsed.scheme != "https":
        return "other"
    if host.endswith(".gov.pk") or any(
        host == domain or host.endswith("." + domain)
        for domains in OFFICIAL_DOMAINS.values() for domain in domains
    ):
        return "official"
    if any(host == domain or host.endswith("." + domain) for domain in _NEWS_DOMAINS):
        return "news"
    return "other"


def _search(claim: str, key: str) -> object:
    payload = {
        "query": claim + " official",
        "topic": "general", "search_depth": "basic", "max_results": 5,
        "auto_parameters": False, "include_answer": False,
        "include_raw_content": False, "include_images": False,
    }
    request = Request(
        "https://api.tavily.com/search",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        raw = response.read(_MAX_RESPONSE_BYTES + 1)
    if len(raw) > _MAX_RESPONSE_BYTES:
        raise ValueError("Oversized search response")
    return json.loads(raw.decode("utf-8"))


def _normalize(statement: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", statement.casefold()))


def _opposite(statement: str) -> str | None:
    # Only explicit auxiliary negation; do not infer contradiction from missing words.
    match = re.search(r"\b(has|have|had|will|is|are|was|were)\s+(not\s+)?", statement, re.I)
    if not match:
        return None
    replacement = match[1] + (" " if match[2] else " not ")
    return statement[:match.start()] + replacement + statement[match.end():]


def _decide(claim: str, evidence: list[ClaimSource]) -> ClaimStatus:
    # Search snippets do not resolve dates relative to the original message.
    if re.search(r"\b(today|tomorrow|yesterday|next|this|last|currently|now)\b", claim, re.I):
        return "insufficient_evidence"
    target = _normalize(claim)
    opposite = _opposite(claim)
    if len(target.split()) < 5:
        return "insufficient_evidence"
    support = contradiction = False
    for source in evidence:
        # News is useful context, but automatic verdicts require official evidence.
        if source.source_kind != "official":
            continue
        for sentence in sentences(source.snippet):
            if any(char in sentence for char in ('"', "?", "\u201c", "\u201d")):
                continue
            normalized = _normalize(sentence)
            support |= normalized == target
            contradiction |= opposite is not None and normalized == _normalize(opposite)
    if support and contradiction:
        return "conflicting"
    if support:
        return "confirmed"
    if contradiction:
        return "contradicted"
    return "insufficient_evidence"


def verify_claim(claim: str) -> ClaimVerification:
    """One basic search with safe failures and conservative snippet evaluation."""
    claim = claim.strip()
    if not claim or len(claim) > 500:
        return ClaimVerification(claim=claim, explanation="A claim of 1 to 500 characters is required.")
    key = os.getenv("TAVILY_API_KEY", "").strip()
    if not key or key == "your_tavily_api_key_here":
        return ClaimVerification(claim=claim, explanation="Tavily API key is not configured.")
    try:
        result = _search(claim, key)
    except (URLError, OSError, HTTPException, ValueError, UnicodeError):
        return ClaimVerification(claim=claim, explanation="Search was unavailable or returned unreadable data.")
    if not isinstance(result, dict) or not isinstance(result.get("results"), list):
        return ClaimVerification(claim=claim, explanation="Search returned malformed result data.")
    evidence: list[ClaimSource] = []
    seen: set[str] = set()
    claim_words = set(_normalize(claim).split()) - {"the", "has", "have", "is", "a", "of", "to", "will", "all"}
    for item in result["results"][:10]:
        if not isinstance(item, dict):
            continue
        if not all(isinstance(item.get(field), str) and item[field].strip() for field in ("title", "url", "content")):
            continue
        try:
            source = ClaimSource(title=item["title"][:300], url=item["url"],
                                 snippet=item["content"][:4000], trusted=False, source_kind="other")
            source.source_kind = _source_kind(str(source.url))
            source.trusted = source.source_kind in {"official", "news"}
        except (ValidationError, ValueError):
            continue
        url = str(source.url)
        overlap = claim_words & set(_normalize(source.snippet).split())
        if url in seen or len(overlap) < min(3, len(claim_words)):
            continue
        seen.add(url)
        evidence.append(source)
    evidence.sort(key=lambda item: {"official": 0, "news": 1, "other": 2}[item.source_kind])
    evidence = evidence[:5]
    status = _decide(claim, evidence)
    return ClaimVerification(
        claim=claim, status=status, evidence=evidence,
        explanation=("No clear official statement match; missing evidence does not mean the claim is false."
                     if status == "insufficient_evidence" else
                     "Based on explicit statement matching in official search snippets, not full-page verification."),
    )
