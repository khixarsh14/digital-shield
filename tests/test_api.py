from unittest.mock import Mock

import pytest

from backend import main
from backend.models.schemas import VerifyResponse


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "digital-shield"}


def test_docs_and_openapi(client):
    redirect = client.get("/", follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "/docs"
    docs = client.get("/docs")
    assert docs.status_code == 200 and "SwaggerUIBundle" in docs.text
    schema = client.get("/openapi.json").json()
    assert {"/verify", "/health", "/analyze-media"} <= schema["paths"].keys()
    assert "content" in schema["components"]["schemas"]["VerifyRequest"]["required"]


@pytest.mark.parametrize("content,language,status", [
    ("Can you send me the assignment PDF when you get home?", "en", "green"),
    ("Your bank account will be blocked. Send your OTP immediately.", "en", "red"),
    ("Visit https://www.google.com for information.", "en", "green"),
    ("Register before midnight: https://bisp-payment-example.xyz", "en", "red"),
    ("http://example.com https://bit.ly/demo", "en", "yellow"),
    ("آپ کا اکاؤنٹ بند ہو جائے گا", "ur", "yellow"),
    ("Aap ka account band ho jaye ga", "ur", "yellow"),
    ("Send your OTP now.", "ur", "red"),
])
def test_verify_contract(client, content, language, status):
    response = client.post("/verify", json={"content": content, "language": language})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == status and body["language"] == language
    assert set(body) == {"status", "label", "summary", "reasons", "actions", "sources",
                         "needs_followup", "followup_question", "language"}
    assert body["sources"] == [] and body["needs_followup"] is False
    assert body["followup_question"] is None
    assert len(body["reasons"]) == len(set(body["reasons"]))


@pytest.mark.parametrize("payload", [
    {}, {"content": ""}, {"content": "   "}, {"content": None}, {"content": 12},
    {"content": "test", "language": "fr"}, {"text": "old field"},
    {"content": "test", "session_id": 12}, {"content": "test", "image": "unsupported"},
])
def test_verify_validation(client, payload):
    response = client.post("/verify", json=payload)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_route_delegates_validated_request(client, monkeypatch):
    result = VerifyResponse(status="yellow", label="Verify First", summary="Test", language="en")
    verifier = Mock(return_value=result)
    monkeypatch.setattr(main, "verify_content", verifier)
    response = client.post("/verify", json={"content": " message ", "session_id": "demo"})
    assert response.json() == result.model_dump(mode="json")
    request = verifier.call_args.args[0]
    assert request.content == "message" and request.session_id == "demo" and request.language == "en"
    verifier.assert_called_once()


@pytest.mark.parametrize("origin", ["http://localhost:5173", "http://127.0.0.1:5173"])
def test_cors(client, origin):
    response = client.options("/verify", headers={"Origin": origin, "Access-Control-Request-Method": "POST"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
