from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

from auth import LocalAuthService
from main import create_app
from store import InMemoryStore


API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

import production_entrypoint  # noqa: E402


def _production_environment(monkeypatch):
    monkeypatch.setenv("RECYCLEROS_DEPLOYMENT_MODE", "production")
    monkeypatch.setenv("RECYCLEROS_TRUSTED_HOSTS", "api.example.com")
    monkeypatch.setenv("RECYCLEROS_CORS_ORIGIN_REGEX", "a^")


def test_production_rejects_wildcard_trusted_host(monkeypatch):
    _production_environment(monkeypatch)
    monkeypatch.setenv("RECYCLEROS_TRUSTED_HOSTS", "*.example.com")

    with pytest.raises(RuntimeError, match="without wildcards"):
        create_app(store=InMemoryStore(), auth_service=LocalAuthService([]))


def test_production_rejects_insecure_browser_origin(monkeypatch):
    _production_environment(monkeypatch)
    monkeypatch.setenv("RECYCLEROS_CORS_ORIGINS", "http://app.example.com")

    with pytest.raises(RuntimeError, match="exact HTTPS origins"):
        create_app(store=InMemoryStore(), auth_service=LocalAuthService([]))


def test_production_hides_docs_and_adds_security_headers(monkeypatch):
    _production_environment(monkeypatch)
    monkeypatch.setenv("RECYCLEROS_CORS_ORIGINS", "https://app.example.com")
    monkeypatch.setenv("RECYCLEROS_RELEASE_SHA", "a" * 40)

    with TestClient(
        create_app(store=InMemoryStore(), auth_service=LocalAuthService([])),
        base_url="https://api.example.com",
    ) as client:
        health = client.get("/v1/health")
        docs = client.get("/docs")
        openapi = client.get("/openapi.json")

    assert health.status_code == 200
    assert health.json()["release"] == "a" * 40
    assert health.headers["cache-control"] == "no-store"
    assert health.headers["strict-transport-security"].startswith("max-age=")
    assert health.headers["x-content-type-options"] == "nosniff"
    assert docs.status_code == 404
    assert openapi.status_code == 404


def test_production_entrypoint_requires_release_and_trusted_proxy(
    monkeypatch,
    tmp_path,
):
    database_secret = tmp_path / "database_url"
    database_secret.write_text("postgresql://production", encoding="utf-8")
    monkeypatch.setenv("RECYCLEROS_DEPLOYMENT_MODE", "production")
    monkeypatch.setenv("DATABASE_URL_FILE", str(database_secret))
    monkeypatch.setenv("RECYCLEROS_RELEASE_SHA", "b" * 40)
    monkeypatch.setenv("RECYCLEROS_FORWARDED_ALLOW_IPS", "10.0.0.10")
    monkeypatch.setenv("RECYCLEROS_API_WORKERS", "3")

    command = production_entrypoint.build_command(tmp_path)

    assert command[command.index("--workers") + 1] == "3"
    assert command[command.index("--forwarded-allow-ips") + 1] == "10.0.0.10"

    monkeypatch.setenv("RECYCLEROS_FORWARDED_ALLOW_IPS", "*")
    with pytest.raises(RuntimeError, match="trusted proxies"):
        production_entrypoint.build_command(tmp_path)
