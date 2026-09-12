import pytest

from backend.tools.url_checker import check_url, extract_urls


@pytest.mark.parametrize("url,signals", [
    ("https://www.google.com", set()),
    ("http://localhost:5173", set()),
    ("http://127.0.0.1:5173", set()),
    ("http://[::1]:5173", set()),
    ("https://portal.bisp.gov.pk/login", set()),
    ("http://192.168.1.20/login", {"missing_https", "ip_address"}),
    ("https://bit.ly/example", {"shortener"}),
    ("https://bisp-payment-example.xyz", {"brand_mismatch", "suspicious_tld"}),
    ("https://bisp.gov.pk.evil.example/login", {"brand_mismatch", "excessive_subdomains"}),
    ("https://n4dra-login.example", {"brand_mismatch"}),
    ("https://example.com/login", set()),
    ("https://bisp.gov.pk@evil.example", {"embedded_credentials"}),
    ("https://bad.example:99999", {"invalid_url"}),
    ("https://[broken", {"invalid_url"}),
])
def test_url_evidence(url, signals):
    evidence = check_url(url)
    assert set(evidence.signals) == signals
    assert evidence.score == len(evidence.signals) == len(evidence.reasons)
    assert evidence == check_url(url)


def test_extraction_punctuation_duplicates_and_balanced_parentheses():
    content = "See (https://www.google.com), https://bit.ly/demo. https://bit.ly/demo! www.example.com"
    assert extract_urls(content) == ["https://www.google.com", "https://bit.ly/demo", "www.example.com"]
    assert extract_urls("https://en.example/wiki/Test_(one).") == ["https://en.example/wiki/Test_(one)"]
    assert extract_urls("Send the assignment PDF.") == []
