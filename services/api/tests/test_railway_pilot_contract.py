from copy import deepcopy
import json
from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPOSITORY_ROOT / "tools" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from railway_pilot_contract import (  # noqa: E402
    validate_contract,
    validate_deployment_identity,
    validate_railway_config,
    validate_variable_template,
)


PILOT_DIR = REPOSITORY_ROOT / "deploy" / "railway" / "pilot"


def _contract() -> dict:
    return json.loads((PILOT_DIR / "pilot.contract.json").read_text(encoding="utf-8"))


def _config() -> dict:
    return json.loads((PILOT_DIR / "railway.json").read_text(encoding="utf-8"))


def _variables() -> str:
    return (PILOT_DIR / "variables.example").read_text(encoding="utf-8")


def _ready_contract() -> dict:
    contract = deepcopy(_contract())
    contract["lifecycle"] = "verified"
    contract["provider"]["project_id"] = "railway-project-123"
    contract["cost_controls"]["alert_verified"] = True
    contract["cost_controls"]["hard_limit_verified"] = True
    contract["runtime"]["public_access_enabled"] = True
    contract["runtime"]["api_url"] = "https://recycleros-pilot.up.railway.app"
    contract["runtime"]["release_commit"] = "a" * 40
    contract["database"]["daily_backup_enabled"] = True
    contract["database"]["weekly_backup_enabled"] = True
    contract["database"]["off_platform_backup_enabled"] = True
    contract["database"]["restore_rehearsal_evidence"] = "restore-run-100"
    contract["security"]["sealed_variables"] = True
    contract["security"]["two_factor_authentication"] = True
    contract["observability"]["uptime_check_configured"] = True
    contract["observability"]["alert_delivery_verified"] = True
    contract["approvals"] = {
        "deployment": True,
        "field_access": True,
        "restore_owner_assigned": True,
        "support_owner_assigned": True,
    }
    return contract


def test_planned_railway_pilot_is_structurally_valid():
    assert validate_contract(_contract()) == []
    assert validate_railway_config(_config()) == []
    assert validate_variable_template(_variables()) == []


def test_planned_contract_is_not_field_ready():
    errors = validate_contract(_contract(), require_ready=True)

    assert "lifecycle must be verified for field readiness" in errors
    assert "database.daily_backup_enabled must be true" in errors
    assert "database.off_platform_backup_enabled must be true" in errors


def test_verified_contract_passes_field_readiness():
    assert validate_contract(_ready_contract(), require_ready=True) == []


def test_verified_lifecycle_cannot_bypass_readiness_in_normal_ci():
    contract = _contract()
    contract["lifecycle"] = "verified"

    errors = validate_contract(contract)

    assert "database.daily_backup_enabled must be true" in errors
    assert "database.restore_rehearsal_evidence is required" in errors
    assert "approvals.field_access must be true" in errors


def test_contract_rejects_credentials_and_cost_drift():
    contract = _contract()
    contract["provider_token"] = "embedded-secret"
    contract["cost_controls"]["hard_limit_usd"] = 100

    errors = validate_contract(contract)

    assert any("Credential fields are forbidden" in error for error in errors)
    assert "cost_controls.hard_limit_usd must be 30" in errors


def test_config_rejects_scale_and_public_database_drift():
    config = _config()
    config["deploy"]["numReplicas"] = 3
    contract = _contract()
    contract["database"]["tcp_proxy_enabled"] = True

    assert "deploy.numReplicas must be 1" in validate_railway_config(config)
    assert "database.tcp_proxy_enabled must be False" in validate_contract(contract)


def test_variable_template_rejects_literal_secrets():
    variables = _variables().replace(
        "${{Postgres.DATABASE_URL}}",
        "postgresql://user:password@example.invalid/database",
    )

    errors = validate_variable_template(variables)

    assert "DATABASE_URL must use the approved Railway value or placeholder" in errors


def test_docker_healthcheck_uses_platform_port():
    dockerfile = (REPOSITORY_ROOT / "services" / "api" / "Dockerfile").read_text(
        encoding="utf-8"
    )

    assert "os.getenv('PORT', '8000')" in dockerfile


def test_acceptance_inputs_must_match_committed_deployment_identity():
    contract = _ready_contract()

    assert validate_deployment_identity(
        contract,
        expected_api_url=contract["runtime"]["api_url"],
        expected_release_sha=contract["runtime"]["release_commit"],
    ) == []
    assert validate_deployment_identity(
        contract,
        expected_api_url="https://wrong-release.up.railway.app",
        expected_release_sha="b" * 40,
    ) == [
        "Workflow input does not match contract: runtime.api_url",
        "Workflow input does not match contract: runtime.release_commit",
    ]


def test_uptime_monitor_is_cost_bounded_and_reports_incidents():
    workflow = (
        REPOSITORY_ROOT / ".github" / "workflows" / "railway-pilot-monitor.yml"
    ).read_text(encoding="utf-8")

    assert 'cron: "37 */2 * * *"' in workflow
    assert "production_endpoint_verify.py" in workflow
    assert "issues: write" in workflow
    assert "simulate_failure" in workflow
    assert "gh issue create" in workflow
    assert "gh issue close" in workflow
