"""Local URL heuristics only: never fetch, resolve, or follow a URL."""

from dataclasses import dataclass
from ipaddress import ip_address
import re
from typing import Literal
from urllib.parse import unquote, urlsplit


URLSignal = Literal[
    "invalid_url", "missing_https", "ip_address", "excessive_subdomains",
    "shortener", "suspicious_tld", "suspicious_keywords", "brand_mismatch",
    "embedded_credentials", "confusing_url",
]

# Small demo reference supplied in the project brief, not an exhaustive registry.
OFFICIAL_DOMAINS = {
    "bisp": {"bisp.gov.pk"},
    "nadra": {"nadra.gov.pk"},
    "hec": {"hec.gov.pk"},
}
_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "shorturl.at"}
_CAUTION_TLDS = {"xyz", "top", "click", "work", "zip"}
_URL_PATTERN = re.compile(r"\b(?:https?://|www\.)[^\s<>\"'`]+", re.IGNORECASE)


@dataclass(frozen=True)
class URLEvidence:
    url: str
    signals: tuple[URLSignal, ...]
    reasons: tuple[str, ...]
    score: int


def extract_urls(content: str) -> list[str]:
    """Extract HTTP(S)/www links in order, trimming prose punctuation."""
    urls: list[str] = []
    for match in _URL_PATTERN.finditer(content):
        url = match.group().rstrip(".,;:!?،۔")
        for opening, closing in (("(", ")"), ("[", "]"), ("{", "}")):
            while url.endswith(closing) and url.count(closing) > url.count(opening):
                url = url[:-1]
        if url not in urls:
            urls.append(url)
    return urls


def _matches_domain(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def check_url(url: str) -> URLEvidence:
    signals: list[URLSignal] = []
    reasons: list[str] = []

    def add(signal: URLSignal, reason: str) -> None:
        signals.append(signal)
        reasons.append(reason)

    try:
        parsed = urlsplit("http://" + url if url.lower().startswith("www.") else url)
        host = (parsed.hostname or "").rstrip(".").lower()
        _ = parsed.port  # Validate malformed/out-of-range ports without connecting.
        if parsed.scheme.lower() not in {"http", "https"} or not host:
            raise ValueError("Unsupported or missing host")
        if any(char.isspace() for char in url) or "\\" in url:
            raise ValueError("Ambiguous URL")
        ascii_host = host.encode("idna").decode("ascii")
        try:
            address = ip_address(ascii_host)
        except ValueError:
            address = None
            if not all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
                       for label in ascii_host.split(".")):
                raise ValueError("Invalid hostname")
    except (ValueError, UnicodeError):
        return URLEvidence(url, ("invalid_url",), ("A link could not be read as a valid web address.",), 1)

    # Only exact localhost names and loopback IPs are development exceptions.
    local = ascii_host == "localhost" or ascii_host.endswith(".localhost") or (
        address is not None and address.is_loopback
    )
    if parsed.username is not None or parsed.password is not None:
        add("embedded_credentials", "A link includes text before @ that can disguise its destination.")
    if not local:
        if parsed.scheme.lower() != "https":
            add("missing_https", "A link does not use an encrypted HTTPS connection.")
        if address is not None:
            add("ip_address", "A link uses a numeric address instead of an organization's website name.")
        else:
            labels = ascii_host.split(".")
            suffix_size = 3 if ascii_host.endswith((".gov.pk", ".com.pk", ".org.pk", ".edu.pk", ".co.uk")) else 2
            if len(labels) - suffix_size >= 3:
                add("excessive_subdomains", "A link has many website-name sections, which can hide its destination.")
            if any(_matches_domain(ascii_host, domain) for domain in _SHORTENERS):
                add("shortener", "A shortened link hides the destination until it is opened.")
            if labels[-1] in _CAUTION_TLDS:
                add("suspicious_tld", "A link uses an ending on this demo's caution list; that alone does not make it unsafe.")
            tokens = set(re.findall(r"[a-z0-9]+", ascii_host))
            lookalikes = {token.translate(str.maketrans({"1": "i", "4": "a", "3": "e", "0": "o"})) for token in tokens}
            for brand, domains in OFFICIAL_DOMAINS.items():
                if (brand in tokens or brand in lookalikes) and not any(
                    _matches_domain(ascii_host, domain) for domain in domains
                ):
                    add("brand_mismatch", "A link mentions or resembles a known organization but does not match its demo reference domain.")
                    break
            known_official = any(_matches_domain(ascii_host, domain)
                                 for domains in OFFICIAL_DOMAINS.values() for domain in domains)
            words = set(re.findall(r"[a-z]+", unquote(ascii_host + parsed.path).lower()))
            if not known_official and len(words & {"login", "verify", "payment", "reward", "claim", "secure", "account", "update", "password"}) >= 2:
                add("suspicious_keywords", "A link combines words about accounts, payments, or rewards that deserve checking.")
    if len(url) > 200 or "%" in parsed.netloc or "xn--" in ascii_host or host != ascii_host:
        add("confusing_url", "A link is unusually long or uses an encoded website name that may be difficult to recognize.")
    return URLEvidence(url, tuple(signals), tuple(reasons), len(signals))
