import socket

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(autouse=True)
def offline_environment(monkeypatch):
    """No real keys or external connections in the normal suite."""
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("MAX_MEDIA_UPLOAD_MB", raising=False)

    connect = socket.socket.connect
    connect_ex = socket.socket.connect_ex

    def local_only(original):
        def guarded(sock, address):
            # Windows asyncio uses loopback socket pairs internally.
            if isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
                return original(sock, address)
            raise AssertionError("External network access is disabled; mock the provider transport.")
        return guarded

    monkeypatch.setattr(socket.socket, "connect", local_only(connect))
    monkeypatch.setattr(socket.socket, "connect_ex", local_only(connect_ex))


@pytest.fixture
def client():
    with TestClient(app) as instance:
        yield instance
