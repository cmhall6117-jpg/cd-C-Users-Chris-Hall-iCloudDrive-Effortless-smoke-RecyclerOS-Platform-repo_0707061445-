import pytest
from fastapi.testclient import TestClient

from auth import LocalAuthService
from main import create_app
from runtime_config import read_config_value
from store import InMemoryStore


class NotReadyStore(InMemoryStore):
    storage_name = "not-ready-test"

    def check_readiness(self) -> bool:
        return False


def test_liveness_and_readiness_are_separate():
    with TestClient(create_app()) as client:
        live = client.get("/v1/health/live")
        ready = client.get("/v1/health/ready")

    assert live.status_code == 200
    assert live.json()["status"] == "alive"
    assert ready.status_code == 200
    assert ready.json() == {
        "status": "ready",
        "storage": "ready",
        "auth": "ready",
    }


def test_readiness_fails_without_hiding_liveness():
    with TestClient(
        create_app(store=NotReadyStore(), auth_service=LocalAuthService([]))
    ) as client:
        ready = client.get("/v1/health/ready")
        live = client.get("/v1/health/live")

    assert ready.status_code == 503
    assert ready.json()["storage"] == "not_ready"
    assert live.status_code == 200


def test_config_value_reads_secret_file(tmp_path):
    secret_file = tmp_path / "database-url"
    secret_file.write_text("postgresql://pilot-secret\n", encoding="utf-8")

    assert read_config_value(
        "DATABASE_URL",
        environ={"DATABASE_URL_FILE": str(secret_file)},
    ) == "postgresql://pilot-secret"


def test_config_value_rejects_ambiguous_sources(tmp_path):
    secret_file = tmp_path / "database-url"
    secret_file.write_text("file-secret", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Set only one"):
        read_config_value(
            "DATABASE_URL",
            environ={
                "DATABASE_URL": "direct-secret",
                "DATABASE_URL_FILE": str(secret_file),
            },
        )


def test_production_mode_requires_trusted_hosts(monkeypatch):
    monkeypatch.setenv("RECYCLEROS_DEPLOYMENT_MODE", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_FILE", raising=False)
    monkeypatch.delenv("RECYCLEROS_TRUSTED_HOSTS", raising=False)

    with pytest.raises(RuntimeError, match="RECYCLEROS_TRUSTED_HOSTS"):
        create_app(store=InMemoryStore(), auth_service=LocalAuthService([]))
