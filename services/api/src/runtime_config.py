from collections.abc import Mapping
import os
from pathlib import Path
from urllib.parse import urlsplit


def read_config_value(
    name: str,
    *,
    default: str | None = None,
    required: bool = False,
    environ: Mapping[str, str] | None = None,
) -> str | None:
    """Read NAME or NAME_FILE without allowing ambiguous secret sources."""
    values = os.environ if environ is None else environ
    direct_value = values.get(name)
    file_name = values.get(f"{name}_FILE")
    if direct_value is not None and file_name is not None:
        raise RuntimeError(f"Set only one of {name} or {name}_FILE.")

    value = direct_value
    if file_name is not None:
        try:
            value = Path(file_name).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(f"Unable to read {name}_FILE.") from exc

    if value is not None:
        value = value.strip()
    if not value:
        value = default
    if required and not value:
        raise RuntimeError(f"{name} or {name}_FILE is required.")
    return value


def read_csv_config(
    name: str,
    *,
    environ: Mapping[str, str] | None = None,
) -> list[str]:
    values = os.environ if environ is None else environ
    return [item.strip() for item in values.get(name, "").split(",") if item.strip()]


def validate_production_web_config(
    *,
    trusted_hosts: list[str],
    cors_origins: list[str],
    cors_origin_regex: str | None,
) -> None:
    if not trusted_hosts:
        raise RuntimeError("Production mode requires RECYCLEROS_TRUSTED_HOSTS.")

    for host in trusted_hosts:
        if any(character.isspace() for character in host):
            raise RuntimeError("Production trusted hosts cannot contain whitespace.")
        if "*" in host or "://" in host or "/" in host:
            raise RuntimeError(
                "Production trusted hosts must be exact hostnames without wildcards."
            )
        try:
            parsed_host = urlsplit(f"//{host}")
            parsed_host.port
        except ValueError as exc:
            raise RuntimeError("Production trusted host has an invalid port.") from exc
        if (
            not parsed_host.hostname
            or parsed_host.username
            or parsed_host.password
            or parsed_host.query
            or parsed_host.fragment
        ):
            raise RuntimeError("Production trusted host is invalid.")

    for origin in cors_origins:
        parsed_origin = urlsplit(origin)
        try:
            parsed_origin.port
        except ValueError as exc:
            raise RuntimeError("Production CORS origin has an invalid port.") from exc
        if (
            parsed_origin.scheme != "https"
            or not parsed_origin.hostname
            or parsed_origin.username
            or parsed_origin.password
            or parsed_origin.path
            or parsed_origin.query
            or parsed_origin.fragment
        ):
            raise RuntimeError(
                "Production CORS origins must be exact HTTPS origins without paths."
            )

    if cors_origin_regex not in (None, "", "a^"):
        raise RuntimeError(
            "Production mode does not allow a permissive CORS origin regex."
        )
