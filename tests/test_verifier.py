"""Run with python -m unittest discover -s tests."""

import unittest
from unittest.mock import call, patch

from backend.agent import verifier
from backend.models.schemas import VerifyRequest


class VerifierTests(unittest.TestCase):
    def test_unsupported_urdu_never_falls_through_to_green(self):
        for content in ["آپ کا اکاؤنٹ بند ہو جائے گا", "Aap ka account band ho jaye ga"]:
            with self.subTest(content=content):
                result = verifier.verify_content(VerifyRequest(content=content, language="ur"))
                self.assertEqual(result.status, "yellow")
                self.assertEqual(result.label, "Verify First")
                self.assertEqual(result.language, "ur")
                self.assertIn("Only English scam patterns", result.summary)
                self.assertIn("could not be fully checked", result.summary)

    def test_urdu_credential_evidence_remains_red(self):
        result = verifier.verify_content(VerifyRequest(content="Send your OTP immediately.", language="ur"))
        self.assertEqual(result.status, "red")
        self.assertEqual(result.language, "ur")

    def test_url_reasons_use_plain_apostrophes(self):
        result = verifier.verify_content(VerifyRequest(
            content="BISP has announced a new payment. Register before midnight: https://bisp-payment-example.xyz"
        ))
        self.assertEqual(result.status, "red")
        self.assertIn("A link uses an ending on this demo's caution list; that alone does not make it unsafe.", result.reasons)
        ip_result = verifier.check_url("http://192.168.1.20/login")
        self.assertIn("A link uses a numeric address instead of an organization's website name.", ip_result.reasons)
        for reason in [*result.reasons, *ip_result.reasons]:
            self.assertTrue(reason.isascii(), reason)

    def test_plain_text_does_not_call_url_checker(self):
        content = "Can you send me the assignment PDF when you get home?"
        with patch.object(verifier, "check_scam", wraps=verifier.check_scam) as scam, \
                patch.object(verifier, "check_url", wraps=verifier.check_url) as url:
            result = verifier.verify_content(VerifyRequest(content=content))
        scam.assert_called_once_with(content)
        url.assert_not_called()
        self.assertEqual(result.status, "green")
        self.assertEqual(result.reasons, [])

    def test_all_distinct_urls_are_checked(self):
        good = "https://www.google.com"
        bad = "https://bisp-payment-example.xyz"
        content = f"Register before midnight: {good} {bad} {good}"
        with patch.object(verifier, "check_scam", wraps=verifier.check_scam) as scam, \
                patch.object(verifier, "check_url", wraps=verifier.check_url) as url:
            result = verifier.verify_content(VerifyRequest(content=content))
        scam.assert_called_once_with(content)
        self.assertEqual(url.call_args_list, [call(good), call(bad)])
        self.assertEqual(result.status, "red")
        self.assertEqual(len(result.reasons), len(set(result.reasons)))

    def test_risk_and_language_regressions(self):
        cases = [
            ("Your bank account will be blocked. Send your OTP immediately.", "en", "red"),
            ("Visit https://www.google.com for more information.", "en", "green"),
            ("Claim your reward here: https://bit.ly/example", "en", "red"),
            ("http://example.com https://bit.ly/demo", "en", "yellow"),
            ("آپ کا اکاؤنٹ بند ہو جائے گا", "ur", "yellow"),
        ]
        for content, language, expected in cases:
            with self.subTest(content=content):
                result = verifier.verify_content(VerifyRequest(content=content, language=language))
                self.assertEqual(result.status, expected)
                self.assertEqual(result.language, language)
                self.assertEqual(result.sources, [])
                self.assertFalse(result.needs_followup)
                self.assertIsNone(result.followup_question)


if __name__ == "__main__":
    unittest.main()
