import json
from http.client import IncompleteRead
import os
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from backend.tools.claim_detector import detect_claim
from backend.tools import claim_verifier as tool


CLAIM = "BISP has launched a new Rs. 25,000 payment scheme."
DENIAL = "BISP has not launched a new Rs. 25,000 payment scheme."


def result(content=CLAIM, url="https://bisp.gov.pk/notice"):
    return {"title": "Payment scheme notice", "url": url, "content": content}


class ClaimDetectorTests(unittest.TestCase):
    def test_claims(self):
        for text in ["HEC has announced all universities will remain closed next week.",
                     CLAIM, "NADRA has made CNIC renewal free this month."]:
            with self.subTest(text=text):
                candidate = detect_claim(text)
                self.assertTrue(candidate.has_claim)
                self.assertEqual(candidate.claim, text)

    def test_nonclaims(self):
        for text in ["Send your OTP immediately.", "Can you send me the assignment PDF?",
                     "Click this link now.", "Please check whether HEC has announced closures.",
                     "HEC has announced closures?", "The bank payment arrived."]:
            with self.subTest(text=text):
                self.assertFalse(detect_claim(text).has_claim)
                self.assertIsNone(detect_claim(text).claim)

    def test_extracts_claim_not_instructions(self):
        self.assertEqual(detect_claim("Hello! " + CLAIM + " Send your OTP.").claim, CLAIM)


class ClaimVerifierTests(unittest.TestCase):
    def setUp(self):
        self.key = patch.dict(os.environ, {"TAVILY_API_KEY": "test-only-key"})
        self.key.start()
        self.addCleanup(self.key.stop)

    def verify(self, results, claim=CLAIM):
        with patch.object(tool, "_search", return_value={"results": results}) as search:
            response = tool.verify_claim(claim)
        search.assert_called_once_with(claim, "test-only-key")
        return response

    def test_confirmed(self):
        self.assertEqual(self.verify([result()]).status, "confirmed")

    def test_contradicted(self):
        self.assertEqual(self.verify([result(DENIAL)]).status, "contradicted")

    def test_conflicting(self):
        response = self.verify([result(), result(DENIAL, "https://bisp.gov.pk/correction")])
        self.assertEqual(response.status, "conflicting")

    def test_weak_irrelevant_and_spoofed_evidence(self):
        for item in [result("The weather is sunny."), result(url="https://bisp.gov.pk.evil.example"),
                     result(url="https://bisp.gov.pk@evil.example"), result(url="http://bisp.gov.pk"),
                     result("Some people say " + CLAIM), result('"' + CLAIM + '"'),
                     result(CLAIM.replace("25,000", "50,000"))]:
            with self.subTest(item=item):
                self.assertEqual(self.verify([item]).status, "insufficient_evidence")

    def test_relative_date_is_not_resolved(self):
        claim = "HEC has announced all universities will remain closed next week."
        self.assertEqual(self.verify([result(claim, "https://hec.gov.pk/news")], claim).status,
                         "insufficient_evidence")

    def test_preference_and_news_cannot_confirm_alone(self):
        news = result(url="https://www.dawn.com/news/123")
        other = result(url="https://unknown.example/news")
        response = self.verify([other, news, result(), result()])
        self.assertEqual([item.source_kind for item in response.evidence], ["official", "news", "other"])
        self.assertEqual([item.trusted for item in response.evidence], [True, True, False])
        self.assertEqual(self.verify([news]).status, "insufficient_evidence")

    def test_missing_key_does_not_search(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": ""}), patch.object(tool, "_search") as search:
            response = tool.verify_claim(CLAIM)
        search.assert_not_called()
        self.assertEqual(response.status, "insufficient_evidence")

    def test_search_failure_hides_exception_details(self):
        for error in [URLError("secret-key"), TimeoutError("secret-key"), ValueError("secret-key"), IncompleteRead(b"secret-key")]:
            with patch.object(tool, "_search", side_effect=error):
                response = tool.verify_claim(CLAIM)
            self.assertEqual(response.status, "insufficient_evidence")
            self.assertNotIn("secret-key", response.model_dump_json())

    def test_empty_and_malformed_results(self):
        for data in [None, [], {}, {"results": None}, {"results": []},
                     {"results": [None, {}, result(url="not a URL"), {"content": 12}]}]:
            with patch.object(tool, "_search", return_value=data):
                self.assertEqual(tool.verify_claim(CLAIM).status, "insufficient_evidence")

    def test_http_request_and_unreadable_response(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = json.dumps({"results": [result()]}).encode()
        with patch.object(tool, "urlopen", return_value=response) as transport:
            self.assertEqual(tool.verify_claim(CLAIM).status, "confirmed")
        transport.assert_called_once()
        request = transport.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.tavily.com/search")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-only-key")
        payload = json.loads(request.data)
        self.assertEqual(payload["search_depth"], "basic")
        self.assertFalse(payload["auto_parameters"])
        self.assertFalse(payload["include_answer"])
        self.assertEqual(payload["max_results"], 5)
        self.assertEqual(transport.call_args.kwargs["timeout"], 15)
        response.read.return_value = b"not json"
        with patch.object(tool, "urlopen", return_value=response):
            self.assertEqual(tool.verify_claim(CLAIM).status, "insufficient_evidence")

    def test_invalid_claim_skips_search(self):
        with patch.object(tool, "_search") as search:
            for claim in ["", "  ", "a" * 501]:
                self.assertEqual(tool.verify_claim(claim).status, "insufficient_evidence")
        search.assert_not_called()


if __name__ == "__main__":
    unittest.main()
