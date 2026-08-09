from copy import deepcopy
import json
from pathlib import Path
import sys


SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "tools" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from gcp_pilot_contract import validate_contract  # noqa: E402


CONTRACT_PATH = (
    Path(__file__).resolve().parents[3]
    / "deploy"
    / "gcp"
    / "pilot"
    / "pilot.contract.json"
)


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _ready_contract() -> dict:
    contract = deepcopy(_contract())
    contract["lifecycle"] = "verified"
    contract["cost_controls"]["budget_verified"] = True
    contract["runtime"]["public_access_enabled"] = True
    contract["database"]["restore_rehearsal_evidence"] = "restore-run-100"
    contract["observability"]["uptime_check_provisioned"] = True
    contract["observability"]["alert_delivery_verified"] = True
    contract["approvals"] = {
        "infrastructure_apply": True,
        "field_access": True,
        "restore_owner_assigned": True,
        "support_owner_assigned": True,
    }
    return contract


def test_planned_contract_is_structurally_valid():
    assert validate_contract(_contract()) == []


def test_planned_contract_is_not_field_ready():
    errors = validate_contract(_contract(), require_ready=True)

    assert "lifecycle must be verified for field readiness" in errors
    assert "The Google Cloud budget must be verified" in errors
    assert "Alert delivery must be verified" in errors


def test_verified_contract_passes_field_readiness():
    assert validate_contract(_ready_contract(), require_ready=True) == []


def test_contract_rejects_credentials_and_cost_limit_drift():
    contract = _contract()
    contract["database_url"] = "postgresql://embedded-secret"
    contract["cost_controls"]["monthly_budget_usd"] = 500

    errors = validate_contract(contract)

    assert any("Credential fields are forbidden" in error for error in errors)
    assert "cost_controls.monthly_budget_usd must be 100" in errors


def test_contract_rejects_public_database_and_scale_drift():
    contract = _contract()
    contract["database"]["publicly_accessible"] = True
    contract["runtime"]["maximum_instances"] = 10

    errors = validate_contract(contract)

    assert "database.publicly_accessible must be False" in errors
    assert "runtime.maximum_instances must be 2" in errors
