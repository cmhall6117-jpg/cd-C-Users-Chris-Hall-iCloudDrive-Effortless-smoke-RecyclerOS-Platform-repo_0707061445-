from copy import deepcopy
import json
from pathlib import Path
import sys


SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "tools" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from production_environment_contract import validate_contract  # noqa: E402
from production_database_verify import evaluate_database_snapshot  # noqa: E402
from production_endpoint_verify import evaluate_endpoint  # noqa: E402


EXAMPLE_PATH = (
    Path(__file__).resolve().parents[3]
    / "deploy"
    / "production"
    / "environment.example.json"
)


def _example_contract() -> dict:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def _ready_contract() -> dict:
    contract = deepcopy(_example_contract())
    contract["lifecycle"] = "verified"
    contract["provider"] = {
        "name": "approved-cloud",
        "account_id": "production-account",
        "region": "us-east",
    }
    contract["release"]["image_digest"] = "sha256:" + "a" * 64
    contract["release"]["commit"] = "b" * 40
    contract["network"]["api_url"] = "https://api.recycleros.test"
    contract["network"]["browser_origins"] = ["https://app.recycleros.test"]
    contract["recovery"]["restore_rehearsal_evidence"] = "change-100"
    contract["security"] = {
        "container_registry": "approved-registry",
        "secret_manager": "approved-secret-manager",
        "deployment_role": "recycleros-production-deployer",
        "least_privilege_review": True,
        "image_signing": True,
    }
    contract["observability"] = {
        "log_destination": "central-log-service",
        "metric_destination": "central-metric-service",
        "uptime_check": "uptime-check-100",
        "alert_route": "production-on-call",
    }
    contract["ownership"] = {
        "deployment_owner": "release-manager",
        "restore_owner": "database-owner",
        "incident_commander": "incident-lead",
        "security_approver": "security-owner",
        "business_approver": "business-owner",
    }
    contract["approvals"] = {
        "technical": True,
        "security": True,
        "business": True,
    }
    return contract


def test_example_contract_is_structurally_valid_with_placeholders():
    assert validate_contract(_example_contract(), allow_placeholders=True) == []


def test_example_contract_is_not_launch_ready():
    errors = validate_contract(_example_contract(), require_ready=True)

    assert any("Placeholder" in error for error in errors)
    assert "lifecycle must be verified for launch readiness" in errors


def test_complete_contract_passes_strict_launch_validation():
    assert validate_contract(_ready_contract(), require_ready=True) == []


def test_contract_rejects_credentials_and_public_database():
    contract = _ready_contract()
    contract["database_url"] = "postgresql://secret"
    contract["network"]["database_publicly_accessible"] = True

    errors = validate_contract(contract, require_ready=True)

    assert any("Credential fields are forbidden" in error for error in errors)
    assert "The production database must not be publicly accessible" in errors


def test_contract_rejects_empty_owner_and_invalid_nonplaceholder_origin():
    contract = _example_contract()
    contract["ownership"]["deployment_owner"] = ""
    contract["network"]["browser_origins"] = ["http://app.example.com"]

    errors = validate_contract(contract, allow_placeholders=True)

    assert "ownership.deployment_owner must be a non-empty string" in errors
    assert "Every browser origin must be an exact HTTPS origin" in errors


def test_public_endpoint_acceptance_report_passes_expected_surface():
    release_sha = "c" * 40
    responses = {
        "v1/health/live": {"status": 200, "headers": {}, "json": {"status": "alive"}},
        "v1/health/ready": {"status": 200, "headers": {}, "json": {"status": "ready"}},
        "v1/health": {
            "status": 200,
            "headers": {
                "cache-control": "no-store",
                "referrer-policy": "no-referrer",
                "x-content-type-options": "nosniff",
                "x-frame-options": "DENY",
                "strict-transport-security": "max-age=31536000; includeSubDomains",
            },
            "json": {"release": release_sha},
        },
        "docs": {"status": 404, "headers": {}, "json": None},
        "openapi.json": {"status": 404, "headers": {}, "json": None},
    }

    def fake_fetcher(url: str) -> dict:
        return responses[url.removeprefix("https://api.recycleros.test/")]

    report = evaluate_endpoint(
        base_url="https://api.recycleros.test",
        release_sha=release_sha,
        minimum_certificate_days=14,
        fetcher=fake_fetcher,
        tls_prober=lambda hostname, port: {
            "protocol": "TLSv1.3",
            "days_remaining": 60,
        },
    )

    assert report["passed"] is True


def test_public_endpoint_report_rejects_wrong_release_and_expiring_tls():
    def fake_fetcher(url: str) -> dict:
        path = url.removeprefix("https://api.recycleros.test/")
        if path == "v1/health/live":
            return {"status": 200, "headers": {}, "json": {"status": "alive"}}
        if path == "v1/health/ready":
            return {"status": 200, "headers": {}, "json": {"status": "ready"}}
        if path == "v1/health":
            return {"status": 200, "headers": {}, "json": {"release": "wrong"}}
        return {"status": 404, "headers": {}, "json": None}

    report = evaluate_endpoint(
        base_url="https://api.recycleros.test",
        release_sha="d" * 40,
        minimum_certificate_days=14,
        fetcher=fake_fetcher,
        tls_prober=lambda hostname, port: {
            "protocol": "TLSv1.3",
            "days_remaining": 3,
        },
    )

    failed_checks = {check["name"] for check in report["checks"] if not check["passed"]}
    assert {"tls_certificate", "release_identity", "header_hsts"} <= failed_checks


def test_database_acceptance_requires_tls_limited_role_and_exact_ledger():
    ledger = {"001.sql": "a" * 64}
    snapshot = {
        "server_version_num": 160004,
        "ssl": True,
        "rolsuper": False,
        "rolcreatedb": False,
        "rolcreaterole": False,
        "rolreplication": False,
        "timezone": "UTC",
        "schema_ready": True,
        "active_membership": True,
        "migration_ledger": ledger,
    }

    assert evaluate_database_snapshot(snapshot, ledger)["passed"] is True

    insecure = deepcopy(snapshot)
    insecure["ssl"] = False
    insecure["rolsuper"] = True
    insecure["migration_ledger"] = {"001.sql": "b" * 64}
    report = evaluate_database_snapshot(insecure, ledger)
    failed_checks = {check["name"] for check in report["checks"] if not check["passed"]}

    assert {"tls", "least_privilege_role", "migration_ledger"} <= failed_checks
