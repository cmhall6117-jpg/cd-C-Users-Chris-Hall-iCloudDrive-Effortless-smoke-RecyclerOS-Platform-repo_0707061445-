import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


FORBIDDEN_CREDENTIAL_KEYS = {
    "access_key",
    "client_secret",
    "database_url",
    "password",
    "private_key",
    "service_account_key",
    "token",
}


def _credential_paths(value: Any, path: str = "$") -> list[str]:
    matches: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key.casefold() in FORBIDDEN_CREDENTIAL_KEYS:
                matches.append(child_path)
            matches.extend(_credential_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            matches.extend(_credential_paths(child, f"{path}[{index}]"))
    return matches


def validate_contract(
    contract: dict[str, Any],
    *,
    require_ready: bool = False,
) -> list[str]:
    errors: list[str] = []

    credential_paths = _credential_paths(contract)
    if credential_paths:
        errors.append(
            "Credential fields are forbidden: " + ", ".join(credential_paths)
        )

    if contract.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if contract.get("environment") != "pilot":
        errors.append("environment must be pilot")
    if contract.get("lifecycle") not in {"planned", "verified"}:
        errors.append("lifecycle must be planned or verified")

    provider = contract.get("provider", {})
    if provider.get("name") != "gcp":
        errors.append("provider.name must be gcp")
    project_id = provider.get("project_id", "")
    if not re.fullmatch(r"[a-z][a-z0-9-]{4,28}[a-z0-9]", project_id):
        errors.append("provider.project_id must be a valid Google Cloud project ID")
    if not re.fullmatch(r"\d{6,20}", str(provider.get("project_number", ""))):
        errors.append("provider.project_number must contain only digits")
    if provider.get("region") != "us-east4":
        errors.append("provider.region must be us-east4 for the approved pilot")

    cost = contract.get("cost_controls", {})
    if cost.get("monthly_budget_usd") != 100:
        errors.append("cost_controls.monthly_budget_usd must be 100")
    if cost.get("first_month_ceiling_usd") != 150:
        errors.append("cost_controls.first_month_ceiling_usd must be 150")
    if cost.get("alert_percentages") != [50, 80, 100]:
        errors.append("cost_controls.alert_percentages must be [50, 80, 100]")

    runtime = contract.get("runtime", {})
    if runtime.get("service") != "cloud-run":
        errors.append("runtime.service must be cloud-run")
    if runtime.get("cpu") != 1:
        errors.append("runtime.cpu must be 1")
    if runtime.get("memory") != "1Gi":
        errors.append("runtime.memory must be 1Gi")
    if runtime.get("minimum_instances") != 0:
        errors.append("runtime.minimum_instances must be 0")
    if runtime.get("maximum_instances") != 2:
        errors.append("runtime.maximum_instances must be 2")
    if not 1 <= runtime.get("concurrency", 0) <= 20:
        errors.append("runtime.concurrency must be between 1 and 20")

    database = contract.get("database", {})
    expected_database_values = {
        "service": "cloud-sql",
        "engine": "postgresql",
        "major_version": 16,
        "tier": "db-g1-small",
        "storage_gib": 25,
        "high_availability": False,
        "publicly_accessible": False,
        "deletion_protection": True,
        "backup_retention_days": 14,
        "point_in_time_recovery": True,
    }
    for key, expected in expected_database_values.items():
        if database.get(key) != expected:
            errors.append(f"database.{key} must be {expected!r}")

    security = contract.get("security", {})
    if security.get("secret_manager") != "google-secret-manager":
        errors.append("security.secret_manager must be google-secret-manager")
    if security.get("workload_identity_federation") is not True:
        errors.append("security.workload_identity_federation must be true")
    if security.get("static_service_account_keys") is not False:
        errors.append("security.static_service_account_keys must be false")
    if security.get("terraform_write_only_secrets") is not True:
        errors.append("security.terraform_write_only_secrets must be true")

    testing = contract.get("testing", {})
    if testing.get("maximum_testers") not in {1, 2}:
        errors.append("testing.maximum_testers must be 1 or 2")
    if testing.get("data_policy") != "synthetic_or_authorized_pilot_only":
        errors.append(
            "testing.data_policy must be synthetic_or_authorized_pilot_only"
        )

    if require_ready:
        if contract.get("lifecycle") != "verified":
            errors.append("lifecycle must be verified for field readiness")
        if cost.get("budget_verified") is not True:
            errors.append("The Google Cloud budget must be verified")
        if runtime.get("public_access_enabled") is not True:
            errors.append("The approved pilot API must be accessible to field testers")
        if database.get("restore_rehearsal_evidence") in {"", "PENDING", None}:
            errors.append("A restore rehearsal evidence reference is required")
        observability = contract.get("observability", {})
        if observability.get("uptime_check_provisioned") is not True:
            errors.append("The uptime check must be provisioned")
        if observability.get("alert_delivery_verified") is not True:
            errors.append("Alert delivery must be verified")
        approvals = contract.get("approvals", {})
        for approval in (
            "infrastructure_apply",
            "field_access",
            "restore_owner_assigned",
            "support_owner_assigned",
        ):
            if approvals.get(approval) is not True:
                errors.append(f"approvals.{approval} must be true")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the credential-free RecyclerOS GCP pilot contract."
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("deploy/gcp/pilot/pilot.contract.json"),
    )
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    errors = validate_contract(contract, require_ready=args.require_ready)
    report = {
        "contract": str(args.contract),
        "valid": not errors,
        "field_ready": not validate_contract(contract, require_ready=True),
        "errors": errors,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
