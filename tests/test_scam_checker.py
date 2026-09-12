import pytest

from backend.tools.scam_checker import check_scam


@pytest.mark.parametrize("content,signals", [
    ("Send Rs. 3000 today to confirm your internship.", {"money_request", "urgency"}),
    ("Your bank account will be blocked. Send your OTP immediately.", {"threat", "otp_request", "urgency"}),
    ("Congratulations! You won Rs. 100,000. Pay a processing fee to receive your prize.", {"reward", "money_request"}),
    ("Give me your PIN.", {"credential_request"}),
    ("Please reply today.", {"urgency"}),
    ("This is your bank. Click this link.", {"impersonation", "suspicious_action"}),
    ("I paid my university fee yesterday.", set()),
    ("Can you send me the assignment PDF?", set()),
    ("The bank payment and internship prize were discussed.", set()),
    ("Never share your OTP. Do not send money today.", set()),
    ("Do not share your OTP, but send your password now.", {"credential_request", "urgency"}),
])
def test_scam_evidence(content, signals):
    evidence = check_scam(content)
    assert set(evidence.signals) == signals
    assert evidence.score == len(evidence.signals) == len(evidence.reasons)
    assert evidence == check_scam(content)


def test_repeated_requests_do_not_inflate_score():
    evidence = check_scam("Send your OTP. SEND YOUR OTP.")
    assert evidence.signals == ("otp_request",)
    assert evidence.score == 1
