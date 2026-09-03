from collections.abc import Mapping
import hashlib
import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


def read_secret_setting(
    name: str,
    *,
    environ: Mapping[str, str] | None = None,
) -> str:
    values = os.environ if environ is None else environ
    direct_value = values.get(name)
    file_name = values.get(f"{name}_FILE")
    if direct_value is not None and file_name is not None:
        raise RuntimeError(f"Set only one of {name} or {name}_FILE.")
    if file_name is not None:
        try:
            direct_value = Path(file_name).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(f"Unable to read {name}_FILE.") from exc
    if not direct_value or not direct_value.strip():
        raise RuntimeError(f"{name} or {name}_FILE is required.")
    return direct_value.strip()


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def postgres_command_environment(
    database_url: str,
    *,
    environ: Mapping[str, str] | None = None,
) -> tuple[dict[str, str], str]:
    parsed = urlparse(database_url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise RuntimeError("A PostgreSQL URL is required.")
    database_name = unquote(parsed.path.lstrip("/"))
    if not parsed.hostname or not database_name or not parsed.username:
        raise RuntimeError("PostgreSQL URL must include host, user, and database.")

    command_environment = dict(os.environ if environ is None else environ)
    command_environment.update(
        {
            "PGHOST": parsed.hostname,
            "PGPORT": str(parsed.port or 5432),
            "PGDATABASE": database_name,
            "PGUSER": unquote(parsed.username),
            "PGPASSWORD": unquote(parsed.password or ""),
        }
    )
    query = parse_qs(parsed.query)
    if "sslmode" in query:
        command_environment["PGSSLMODE"] = query["sslmode"][-1]
    return command_environment, database_name
