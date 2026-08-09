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
    "provider_token",
    "token",
}

EXPECTED_VARIABLES = {
    "DATABASE_URL": "${{Postgres.DATABASE_URL}}",
    "RECYCLEROS_DEPLOYMENT_MODE": "production",
    "RECYCLEROS_TRUSTED_HOSTS": (
        "${{RAILWAY_PUBLIC_DOMAIN}},healthcheck.railway.app"
    ),
    "RECYCLEROS_CORS_ORIGINS": "",
    "RECYCLEROS_CORS_ORIGIN_REGEX": "a^",
    "RECYCLEROS_FORWARDED_ALLOW_IPS": "127.0.0.1",
    "RECYCLEROS_API_WORKERS": "1",
    "RECYCLEROS_LOCAL_OPERATOR_PASSWORD": "<GENERATE_AND_SEAL_IN_RAILWAY>",
}

EXPECTED_WATCH_PATTERNS = {
    "services/api/**",
    "database/migrations/postgres/**",
    "tools/scripts/rc1_postgres_migrate.py",
    "deploy/railway/pilot/**",
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


def parse_variable_template(contents: str) -> dict[str, str]:
    variables: dict[str, str] = {}
    for line_number, raw_line in enumerate(contents.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Variable template line {line_number} is invalid.")
        name, value = line.split("=", 1)
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
            raise ValueError(f"Variable template line {line_number} has an invalid name.")
        if name in variables:
            raise ValueError(f"Variable template contains duplicate {name}.")
        variables[name] = value
    return variables


def validate_railway_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if config.get("$schema") != "https://railway.com/railway.schema.json":
        errors.append("railway.json must use the official Railway schema")

    build = config.get("build", {})
    if build.get("builder") != "DOCKERFILE":
        errors.append("build.builder must be DOCKERFILE")
    if build.get("dockerfilePath") != "./services/api/Dockerfile":
        errors.append("build.dockerfilePath must select the hardened API image")
    if set(build.get("watchPatterns", [])) != EXPECTED_WATCH_PATTERNS:
        errors.append("build.watchPatterns must cover the complete API image inputs")

    deploy = config.get("deploy", {})
    expected_values = {
        "numReplicas": 1,
        "healthcheckPath": "/v1/health/ready",
        "healthcheckTimeout": 180,
        "sleepApplication": True,
        "runtime": "V2",
        "restartPolicyType": "ON_FAILURE",
        "restartPolicyMaxRetries": 3,
        "region": "us-east4-eqdc4a",
        "overlapSeconds": 0,
        "drainingSeconds": 15,
        "ipv6EgressEnabled": False,
    }
    for key, expected in expected_values.items():
        if deploy.get(key) != expected:
            errors.append(f"deploy.{key} must be {expected!r}")
    if "startCommand" in deploy:
        errors.append("deploy.startCommand must be omitted to preserve the image entrypoint")

    limits = deploy.get("limitOverride", {}).get("containers", {})
    if limits.get("cpu") != 1:
        errors.append("deploy.limitOverride.containers.cpu must be 1")
    if limits.get("memoryBytes") != 536870912:
        errors.append(
            "deploy.limitOverride.containers.memoryBytes must be 536870912"
        )
    return errors


def validate_variable_template(contents: str) -> list[str]:
    try:
        variables = parse_variable_template(contents)
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    for name, expected in EXPECTED_VARIABLES.items():
        if variables.get(name) != expected:
            errors.append(f"{name} must use the approved Railway value or placeholder")
    unexpected = set(variables) - set(EXPECTED_VARIABLES)
    if unexpected:
        errors.append("Unexpected Railway variables: " + ", ".join(sorted(unexpected)))
    return errors


def validate_deployment_identity(
    contract: dict[str, Any],
    *,
    expected_api_url: str | None = None,
    expected_release_sha: str | None = None,
) -> list[str]:
    errors: list[str] = []
    runtime = contract.get("runtime", {})
    if expected_api_url is not None and runtime.get("api_url") != expected_api_url:
        errors.append("Workflow input does not match contract: runtime.api_url")
    if (
        expected_release_sha is not None
        and runtime.get("release_commit") != expected_release_sha
    ):
        errors.append("Workflow input does not match contract: runtime.release_commit")
    return errors


def validate_contract(
    contract: dict[str, Any],
    *,
    require_ready: bool = False,
) -> list[str]:
    errors: list[str] = []
    credential_paths = _credential_paths(contract)
    if credential_paths:
        errors.append("Credential fields are forbidden: " + ", ".join(credential_paths))

    if contract.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if contract.get("environment") != "pilot":
        errors.append("environment must be pilot")
    if contract.get("lifecycle") not in {"planned", "verified"}:
        errors.append("lifecycle must be planned or verified")

    provider = contract.get("provider", {})
    expected_provider = {
        "name": "railway",
        "plan": "hobby",
        "project_name": "recycleros-pilot",
        "region": "us-east4-eqdc4a",
    }
    for key, expected in expected_provider.items():
        if provider.get(key) != expected:
            errors.append(f"provider.{key} must be {expected!r}")

    cost = contract.get("cost_controls", {})
    expected_cost = {
        "estimated_monthly_min_usd": 12,
        "estimated_monthly_max_usd": 25,
        "alert_usd": 20,
        "hard_limit_usd": 30,
    }
    for key, expected in expected_cost.items():
        if cost.get(key) != expected:
            errors.append(f"cost_controls.{key} must be {expected}")

    runtime = contract.get("runtime", {})
    expected_runtime = {
        "service_name": "recycleros-api",
        "builder": "dockerfile",
        "memory_mib": 512,
        "cpu": 1,
        "replicas": 1,
        "serverless_sleep": True,
        "healthcheck_path": "/v1/health/ready",
    }
    for key, expected in expected_runtime.items():
        if runtime.get(key) != expected:
            errors.append(f"runtime.{key} must be {expected!r}")

    database = contract.get("database", {})
    expected_database = {
        "service_name": "Postgres",
        "engine": "postgresql",
        "major_version": 16,
        "storage_gib": 5,
        "private_database_url": True,
        "tcp_proxy_enabled": False,
        "unmanaged_template_acknowledged": True,
    }
    for key, expected in expected_database.items():
        if database.get(key) != expected:
            errors.append(f"database.{key} must be {expected!r}")

    security = contract.get("security", {})
    if security.get("static_provider_tokens_in_github") is not False:
        errors.append("security.static_provider_tokens_in_github must be false")
    if security.get("exact_trusted_host") is not True:
        errors.append("security.exact_trusted_host must be true")
    if security.get("deployment_branch") != "codex/railway-pilot-environment":
        errors.append("security.deployment_branch must be the Railway pilot branch")

    observability = contract.get("observability", {})
    if observability.get("railway_logs_enabled") is not True:
        errors.append("observability.railway_logs_enabled must be true")

    testing = contract.get("testing", {})
    if testing.get("maximum_testers") not in {1, 2}:
        errors.append("testing.maximum_testers must be 1 or 2")
    if testing.get("data_policy") != "synthetic_or_authorized_pilot_only":
        errors.append("testing.data_policy must be synthetic_or_authorized_pilot_only")

    if require_ready:
        if contract.get("lifecycle") != "verified":
            errors.append("lifecycle must be verified for field readiness")
        if provider.get("project_id") in {"", "PENDING", None}:
            errors.append("provider.project_id must be recorded")
        for name in ("alert_verified", "hard_limit_verified"):
            if cost.get(name) is not True:
                errors.append(f"cost_controls.{name} must be true")
        if runtime.get("public_access_enabled") is not True:
            errors.append("runtime.public_access_enabled must be true")
        api_url = runtime.get("api_url", "")
        if not re.fullmatch(r"https://[a-z0-9-]+\.up\.railway\.app", api_url):
            errors.append("runtime.api_url must be the exact Railway HTTPS origin")
        if not re.fullmatch(r"[0-9a-f]{40}", runtime.get("release_commit", "")):
            errors.append("runtime.release_commit must be a complete Git SHA")
        for name in (
            "daily_backup_enabled",
            "weekly_backup_enabled",
            "off_platform_backup_enabled",
        ):
            if database.get(name) is not True:
                errors.append(f"database.{name} must be true")
        if database.get("restore_rehearsal_evidence") in {"", "PENDING", None}:
            errors.append("database.restore_rehearsal_evidence is required")
        for name in ("sealed_variables", "two_factor_authentication"):
            if security.get(name) is not True:
                errors.append(f"security.{name} must be true")
        for name in ("uptime_check_configured", "alert_delivery_verified"):
            if observability.get(name) is not True:
                errors.append(f"observability.{name} must be true")
        approvals = contract.get("approvals", {})
        for name in (
            "deployment",
            "field_access",
            "restore_owner_assigned",
            "support_owner_assigned",
        ):
            if approvals.get(name) is not True:
                errors.append(f"approvals.{name} must be true")
    elif contract.get("lifecycle") == "verified":
        for error in validate_contract(contract, require_ready=True):
            if error not in errors:
                errors.append(error)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the credential-free RecyclerOS Railway pilot."
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("deploy/railway/pilot/pilot.contract.json"),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("deploy/railway/pilot/railway.json"),
    )
    parser.add_argument(
        "--variables",
        type=Path,
        default=Path("deploy/railway/pilot/variables.example"),
    )
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--expect-api-url")
    parser.add_argument("--expect-release-sha")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    config = json.loads(args.config.read_text(encoding="utf-8"))
    variables = args.variables.read_text(encoding="utf-8")
    errors = validate_contract(contract, require_ready=args.require_ready)
    errors.extend(validate_railway_config(config))
    errors.extend(validate_variable_template(variables))
    errors.extend(
        validate_deployment_identity(
            contract,
            expected_api_url=args.expect_api_url,
            expected_release_sha=args.expect_release_sha,
        )
    )
    readiness_errors = validate_contract(contract, require_ready=True)
    readiness_errors.extend(validate_railway_config(config))
    readiness_errors.extend(validate_variable_template(variables))
    report = {
        "contract": str(args.contract),
        "config": str(args.config),
        "errors": errors,
        "field_ready": not readiness_errors,
        "valid": not errors,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
