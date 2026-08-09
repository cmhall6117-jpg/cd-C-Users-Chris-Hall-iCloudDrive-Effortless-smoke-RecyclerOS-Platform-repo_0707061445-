import argparse
from copy import deepcopy
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


PLACEHOLDER_MARKERS = (
    "unassigned",
    "unselected",
    "unset",
    "replace_with",
    "example.invalid",
)
FORBIDDEN_CREDENTIAL_KEYS = {
    "access_key",
    "client_secret",
    "database_url",
    "password",
    "private_key",
    "token",
}


def _value_at(document: dict, path: str):
    value = document
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(path)
        value = value[part]
    return value


def _is_placeholder(value: object) -> bool:
    return isinstance(value, str) and any(
        marker in value.casefold() for marker in PLACEHOLDER_MARKERS
    )


def _is_exact_https_origin(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    try:
        parsed.port
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.hostname
        and not parsed.username
        and not parsed.password
        and not parsed.path
        and not parsed.query
        and not parsed.fragment
    )


def _credential_paths(value: object, prefix: str = "") -> list[str]:
    paths = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if key.casefold() in FORBIDDEN_CREDENTIAL_KEYS:
                paths.append(path)
            paths.extend(_credential_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_credential_paths(child, f"{prefix}[{index}]"))
    return paths


def _placeholder_paths(value: object, prefix: str = "") -> list[str]:
    paths = []
    if _is_placeholder(value):
        paths.append(prefix or "document")
    elif isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            paths.extend(_placeholder_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_placeholder_paths(child, f"{prefix}[{index}]"))
    return paths


def validate_contract(
    contract: dict,
    *,
    allow_placeholders: bool = False,
    require_ready: bool = False,
) -> list[str]:
    errors: list[str] = []
    required_paths = (
        "schema_version",
        "environment",
        "lifecycle",
        "provider.name",
        "provider.account_id",
        "provider.region",
        "release.image_repository",
        "release.image_digest",
        "release.commit",
        "network.api_url",
        "network.browser_origins",
        "network.trusted_proxy_cidrs",
        "network.database_publicly_accessible",
        "database.engine",
        "database.major_version",
        "database.tls_required",
        "database.encryption_at_rest",
        "database.deletion_protection",
        "database.high_availability",
        "recovery.rpo_hours",
        "recovery.rto_hours",
        "recovery.retention_days",
        "recovery.point_in_time_recovery",
        "recovery.restore_rehearsal_evidence",
        "security.container_registry",
        "security.secret_manager",
        "security.deployment_role",
        "security.least_privilege_review",
        "security.image_signing",
        "observability.log_destination",
        "observability.metric_destination",
        "observability.uptime_check",
        "observability.alert_route",
        "ownership.deployment_owner",
        "ownership.restore_owner",
        "ownership.incident_commander",
        "ownership.security_approver",
        "ownership.business_approver",
        "approvals.technical",
        "approvals.security",
        "approvals.business",
    )
    values: dict[str, object] = {}
    missing_fields = False
    for path in required_paths:
        try:
            values[path] = _value_at(contract, path)
        except KeyError:
            errors.append(f"Missing required field: {path}")
            missing_fields = True

    for path in _credential_paths(contract):
        errors.append(f"Credential fields are forbidden in the contract: {path}")

    if missing_fields:
        return errors

    if values["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if values["environment"] != "production":
        errors.append("environment must be production")
    if values["lifecycle"] not in {"planned", "provisioned", "verified"}:
        errors.append("lifecycle must be planned, provisioned, or verified")
    if require_ready and values["lifecycle"] != "verified":
        errors.append("lifecycle must be verified for launch readiness")

    placeholder_paths = _placeholder_paths(contract)
    if not allow_placeholders:
        errors.extend(f"Placeholder value is not allowed: {path}" for path in placeholder_paths)

    required_text_paths = (
        "provider.name",
        "provider.account_id",
        "provider.region",
        "recovery.restore_rehearsal_evidence",
        "security.container_registry",
        "security.secret_manager",
        "security.deployment_role",
        "observability.log_destination",
        "observability.metric_destination",
        "observability.uptime_check",
        "observability.alert_route",
        "ownership.deployment_owner",
        "ownership.restore_owner",
        "ownership.incident_commander",
        "ownership.security_approver",
        "ownership.business_approver",
    )
    for path in required_text_paths:
        value = values[path]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{path} must be a non-empty string")

    image_repository = values["release.image_repository"]
    if not isinstance(image_repository, str) or not image_repository or "@" in image_repository:
        errors.append("release.image_repository must not contain a digest")
    digest = values["release.image_digest"]
    if not _is_placeholder(digest) and not re.fullmatch(r"sha256:[0-9a-f]{64}", str(digest)):
        errors.append("release.image_digest must be a complete sha256 digest")
    commit = values["release.commit"]
    if not _is_placeholder(commit) and not re.fullmatch(r"[0-9a-f]{40}", str(commit)):
        errors.append("release.commit must be a complete 40-character Git SHA")

    api_url = values["network.api_url"]
    if not _is_placeholder(api_url) and not _is_exact_https_origin(api_url):
        errors.append("network.api_url must be an exact HTTPS origin")
    browser_origins = values["network.browser_origins"]
    if not isinstance(browser_origins, list) or not browser_origins:
        errors.append("network.browser_origins must contain at least one origin")
    else:
        for origin in browser_origins:
            if allow_placeholders and _is_placeholder(origin):
                continue
            if not _is_exact_https_origin(origin):
                errors.append("Every browser origin must be an exact HTTPS origin")
    proxy_cidrs = values["network.trusted_proxy_cidrs"]
    if not isinstance(proxy_cidrs, list) or not proxy_cidrs:
        errors.append("network.trusted_proxy_cidrs must contain at least one network")
    else:
        for network in proxy_cidrs:
            try:
                ipaddress.ip_network(network, strict=False)
            except (TypeError, ValueError):
                errors.append(f"Invalid trusted proxy network: {network}")
    if values["network.database_publicly_accessible"] is not False:
        errors.append("The production database must not be publicly accessible")

    if values["database.engine"] != "postgresql":
        errors.append("database.engine must be postgresql")
    if (
        not isinstance(values["database.major_version"], int)
        or isinstance(values["database.major_version"], bool)
        or values["database.major_version"] < 16
    ):
        errors.append("database.major_version must be at least 16")
    for path in (
        "database.tls_required",
        "database.encryption_at_rest",
        "database.deletion_protection",
        "database.high_availability",
        "recovery.point_in_time_recovery",
    ):
        if values[path] is not True:
            errors.append(f"{path} must be true")

    numeric_limits = {
        "recovery.rpo_hours": (0, 24),
        "recovery.rto_hours": (0, 4),
        "recovery.retention_days": (14, 3650),
    }
    for path, (minimum, maximum) in numeric_limits.items():
        value = values[path]
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not minimum <= value <= maximum
        ):
            errors.append(f"{path} must be between {minimum} and {maximum}")

    if require_ready:
        for path in (
            "security.least_privilege_review",
            "security.image_signing",
            "approvals.technical",
            "approvals.security",
            "approvals.business",
        ):
            if values[path] is not True:
                errors.append(f"{path} must be true for launch readiness")
    return errors


def build_report(
    contract: dict,
    *,
    allow_placeholders: bool,
    require_ready: bool,
) -> dict:
    errors = validate_contract(
        contract,
        allow_placeholders=allow_placeholders,
        require_ready=require_ready,
    )
    report = {
        "schema_version": 1,
        "valid": not errors,
        "launch_ready": not errors and contract.get("lifecycle") == "verified",
        "allow_placeholders": allow_placeholders,
        "errors": errors,
    }
    return deepcopy(report)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a credential-free RecyclerOS production environment contract."
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-placeholders", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--expect-api-url")
    parser.add_argument("--expect-release-sha")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    report = build_report(
        contract,
        allow_placeholders=args.allow_placeholders,
        require_ready=args.require_ready,
    )
    expected_values = {
        "network.api_url": args.expect_api_url,
        "release.commit": args.expect_release_sha,
    }
    for path, expected in expected_values.items():
        if expected is not None and _value_at(contract, path) != expected:
            report["errors"].append(f"Workflow input does not match contract: {path}")
    if report["errors"]:
        report["valid"] = False
        report["launch_ready"] = False
    serialized = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
