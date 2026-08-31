from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tarfile
import tempfile
from typing import Any, Callable

from pilot_postgres_backup import create_backup
from pilot_postgres_common import (
    postgres_command_environment,
    read_secret_setting,
    sha256_file,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIG_KEYS = {
    "schema_version",
    "database_url_file",
    "destination_directory",
    "age_recipient_file",
    "staging_directory",
    "age_executable",
    "pg_dump_executable",
    "keep_daily",
    "keep_weekly",
}
ARTIFACT_PATTERN = re.compile(
    r"^recycleros-pilot-(?P<timestamp>\d{8}T\d{6}Z)-"
    r"(?P<identifier>[0-9a-f]{8})\.tar\.age$"
)


@dataclass(frozen=True)
class OffsiteBackupConfig:
    config_path: Path
    database_url_file: Path
    destination_directory: Path
    age_recipient_file: Path
    staging_directory: Path
    age_executable: str
    pg_dump_executable: str
    keep_daily: int
    keep_weekly: int


@dataclass(frozen=True)
class RuntimeSettings:
    database_url: str
    age_recipient: str
    age_executable: str
    pg_dump_executable: str


@dataclass(frozen=True)
class BackupRecord:
    created_at: datetime
    artifact_path: Path
    envelope_path: Path


@dataclass(frozen=True)
class PublishedBackup:
    artifact_path: Path
    envelope_path: Path
    removed_artifacts: tuple[str, ...]


def _require_string(data: dict[str, Any], name: str) -> str:
    value = data.get(name)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{name} must be a non-empty string.")
    return value.strip()


def _require_count(data: dict[str, Any], name: str, default: int, minimum: int) -> int:
    value = data.get(name, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise RuntimeError(f"{name} must be an integer.")
    if value < minimum or value > 365:
        raise RuntimeError(f"{name} must be between {minimum} and 365.")
    return value


def _absolute_path(value: str, name: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise RuntimeError(f"{name} must be an absolute path.")
    return path.resolve()


def _reject_repository_path(path: Path, name: str, repository_root: Path) -> None:
    repository_root = repository_root.resolve()
    if path == repository_root or path.is_relative_to(repository_root):
        raise RuntimeError(f"{name} must be outside the Git repository.")


def _paths_overlap(first: Path, second: Path) -> bool:
    return (
        first == second
        or first.is_relative_to(second)
        or second.is_relative_to(first)
    )


def load_config(
    config_path: Path,
    *,
    repository_root: Path = REPOSITORY_ROOT,
) -> OffsiteBackupConfig:
    config_path = config_path.expanduser().resolve()
    if not config_path.is_file():
        raise RuntimeError("Off-platform backup config does not exist.")
    _reject_repository_path(config_path, "config_path", repository_root)

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Unable to read off-platform backup config.") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Off-platform backup config must be a JSON object.")
    unknown_keys = sorted(set(data) - CONFIG_KEYS)
    if unknown_keys:
        raise RuntimeError(f"Unknown backup config keys: {', '.join(unknown_keys)}")
    if data.get("schema_version") != 1:
        raise RuntimeError("schema_version must be 1.")

    database_url_file = _absolute_path(
        _require_string(data, "database_url_file"),
        "database_url_file",
    )
    destination_directory = _absolute_path(
        _require_string(data, "destination_directory"),
        "destination_directory",
    )
    age_recipient_file = _absolute_path(
        _require_string(data, "age_recipient_file"),
        "age_recipient_file",
    )
    staging_directory = _absolute_path(
        _require_string(data, "staging_directory"),
        "staging_directory",
    )

    for path, name in (
        (database_url_file, "database_url_file"),
        (destination_directory, "destination_directory"),
        (age_recipient_file, "age_recipient_file"),
    ):
        _reject_repository_path(path, name, repository_root)
    _reject_repository_path(
        staging_directory,
        "staging_directory",
        repository_root,
    )

    if not database_url_file.is_file():
        raise RuntimeError("database_url_file must name an existing file.")
    if not age_recipient_file.is_file():
        raise RuntimeError("age_recipient_file must name an existing file.")
    if not destination_directory.is_dir():
        raise RuntimeError("destination_directory must already exist.")
    if not staging_directory.is_dir():
        raise RuntimeError("staging_directory must already exist.")
    if _paths_overlap(
        destination_directory,
        staging_directory,
    ):
        raise RuntimeError(
            "staging_directory and destination_directory must not overlap."
        )

    age_executable = data.get("age_executable", "age")
    if not isinstance(age_executable, str) or not age_executable.strip():
        raise RuntimeError("age_executable must be a non-empty string.")
    pg_dump_executable = data.get("pg_dump_executable", "pg_dump")
    if not isinstance(pg_dump_executable, str) or not pg_dump_executable.strip():
        raise RuntimeError("pg_dump_executable must be a non-empty string.")

    return OffsiteBackupConfig(
        config_path=config_path,
        database_url_file=database_url_file,
        destination_directory=destination_directory,
        age_recipient_file=age_recipient_file,
        staging_directory=staging_directory,
        age_executable=age_executable.strip(),
        pg_dump_executable=pg_dump_executable.strip(),
        keep_daily=_require_count(data, "keep_daily", 14, 1),
        keep_weekly=_require_count(data, "keep_weekly", 8, 0),
    )


def _read_age_recipient(path: Path) -> str:
    try:
        recipient = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError("Unable to read age_recipient_file.") from exc
    if not recipient or "\n" in recipient or "\r" in recipient:
        raise RuntimeError("age_recipient_file must contain exactly one recipient.")
    if "AGE-SECRET-KEY-" in recipient.upper():
        raise RuntimeError("age_recipient_file must not contain a private identity.")
    if not recipient.startswith(("age1", "ssh-ed25519 ", "ssh-rsa ")):
        raise RuntimeError("age_recipient_file does not contain a supported recipient.")
    return recipient


def validate_runtime(config: OffsiteBackupConfig) -> RuntimeSettings:
    age_executable = shutil.which(config.age_executable)
    if age_executable is None:
        raise RuntimeError("The configured age executable is not available.")
    pg_dump_executable = shutil.which(config.pg_dump_executable)
    if pg_dump_executable is None:
        raise RuntimeError("The configured pg_dump executable is not available.")
    database_url = read_secret_setting(
        "DATABASE_URL",
        environ={"DATABASE_URL_FILE": str(config.database_url_file)},
    )
    postgres_command_environment(database_url, environ={})
    return RuntimeSettings(
        database_url=database_url,
        age_recipient=_read_age_recipient(config.age_recipient_file),
        age_executable=age_executable,
        pg_dump_executable=pg_dump_executable,
    )


def _utc_seconds(value: datetime | None) -> datetime:
    value = datetime.now(timezone.utc) if value is None else value
    if value.tzinfo is None:
        raise RuntimeError("Backup timestamp must include a timezone.")
    return value.astimezone(timezone.utc).replace(microsecond=0)


def _write_bundle(bundle: Path, backup: Path, manifest: Path) -> None:
    with tarfile.open(bundle, mode="w") as archive:
        archive.add(backup, arcname=backup.name, recursive=False)
        archive.add(manifest, arcname=manifest.name, recursive=False)


def _write_bytes_exclusive(path: Path, content: bytes) -> None:
    with path.open("xb") as destination:
        destination.write(content)
        destination.flush()
        os.fsync(destination.fileno())


def _copy_exclusive(source: Path, destination: Path) -> None:
    with source.open("rb") as input_stream, destination.open("xb") as output_stream:
        shutil.copyfileobj(input_stream, output_stream, length=1024 * 1024)
        output_stream.flush()
        os.fsync(output_stream.fileno())


def _publish_pair(
    encrypted_bundle: Path,
    envelope: dict[str, Any],
    destination_directory: Path,
) -> tuple[Path, Path]:
    artifact_name = str(envelope["artifact"]["file"])
    artifact_path = destination_directory / artifact_name
    envelope_path = destination_directory / f"{artifact_name}.envelope.json"
    if artifact_path.exists() or envelope_path.exists():
        raise RuntimeError("Refusing to overwrite an off-platform backup.")

    try:
        # The envelope is the commit marker. Consumers ignore an artifact until
        # its exclusively-created envelope is present.
        _copy_exclusive(encrypted_bundle, artifact_path)
        expected_digest = str(envelope["artifact"]["sha256"])
        if sha256_file(artifact_path) != expected_digest:
            raise RuntimeError("Published encrypted backup checksum mismatch.")
        _write_bytes_exclusive(
            envelope_path,
            (json.dumps(envelope, indent=2) + "\n").encode("utf-8"),
        )
    except Exception:
        for path in (envelope_path, artifact_path):
            if path.exists():
                path.unlink()
        raise
    return artifact_path, envelope_path


def _load_record(envelope_path: Path) -> BackupRecord | None:
    envelope_suffix = ".envelope.json"
    if envelope_path.is_symlink() or not envelope_path.name.endswith(envelope_suffix):
        return None
    artifact_name = envelope_path.name[: -len(envelope_suffix)]
    match = ARTIFACT_PATTERN.fullmatch(artifact_name)
    if match is None:
        return None
    artifact_path = envelope_path.parent / artifact_name
    if artifact_path.is_symlink() or not artifact_path.is_file():
        return None
    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        artifact = envelope["artifact"]
        parsed_time = datetime.fromisoformat(
            str(envelope["created_at"]).replace("Z", "+00:00")
        )
        if parsed_time.tzinfo is None:
            return None
        created_at = parsed_time.astimezone(timezone.utc)
        expected_time = datetime.strptime(
            match.group("timestamp"),
            "%Y%m%dT%H%M%SZ",
        ).replace(tzinfo=timezone.utc)
        valid = (
            envelope.get("schema_version") == 1
            and artifact.get("file") == artifact_name
            and artifact.get("size_bytes") == artifact_path.stat().st_size
            and re.fullmatch(r"[0-9a-f]{64}", str(artifact.get("sha256")))
            is not None
            and envelope.get("encryption") == {
                "tool": "age",
                "mode": "recipient",
            }
            and envelope.get("bundle", {}).get("format") == "tar"
            and created_at == expected_time
        )
    except (
        AttributeError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        return None
    if not valid:
        return None
    return BackupRecord(
        created_at=created_at,
        artifact_path=artifact_path,
        envelope_path=envelope_path,
    )


def apply_retention(
    destination_directory: Path,
    *,
    keep_daily: int,
    keep_weekly: int,
) -> tuple[str, ...]:
    if keep_daily < 1 or keep_weekly < 0:
        raise RuntimeError("Retention requires at least one daily recovery point.")
    records = []
    for envelope_path in destination_directory.iterdir():
        record = _load_record(envelope_path)
        if record is not None:
            records.append(record)
    records.sort(key=lambda record: record.created_at, reverse=True)

    retained = set(records[:keep_daily])
    weekly_periods: set[tuple[int, int]] = set()
    for record in records[keep_daily:]:
        iso_year, iso_week, _ = record.created_at.isocalendar()
        period = (iso_year, iso_week)
        if period not in weekly_periods and len(weekly_periods) < keep_weekly:
            retained.add(record)
            weekly_periods.add(period)

    removed = []
    for record in records:
        if record in retained:
            continue
        record.artifact_path.unlink()
        record.envelope_path.unlink()
        removed.append(record.artifact_path.name)
    return tuple(removed)


def create_offsite_backup(
    config: OffsiteBackupConfig,
    *,
    now: datetime | None = None,
    artifact_id: str | None = None,
    age_runner: Callable[..., Any] | None = None,
    backup_creator: Callable[..., Path] | None = None,
) -> PublishedBackup:
    runtime = validate_runtime(config)
    now = _utc_seconds(now)
    artifact_id = secrets.token_hex(4) if artifact_id is None else artifact_id
    if re.fullmatch(r"[0-9a-f]{8}", artifact_id) is None:
        raise RuntimeError("artifact_id must contain eight lowercase hex characters.")
    age_runner = subprocess.run if age_runner is None else age_runner
    backup_creator = create_backup if backup_creator is None else backup_creator

    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    artifact_name = f"recycleros-pilot-{timestamp}-{artifact_id}.tar.age"
    with tempfile.TemporaryDirectory(
        prefix="recycleros-offsite-",
        dir=config.staging_directory,
    ) as temporary_name:
        temporary = Path(temporary_name)
        backup = temporary / "recycleros-pilot.dump"
        backup_manifest = backup_creator(
            backup,
            database_url=runtime.database_url,
            pg_dump_executable=runtime.pg_dump_executable,
        )
        bundle = temporary / "recycleros-pilot.tar"
        encrypted_bundle = temporary / artifact_name
        _write_bundle(bundle, backup, backup_manifest)
        age_runner(
            [
                runtime.age_executable,
                "--encrypt",
                "--recipient",
                runtime.age_recipient,
                "--output",
                str(encrypted_bundle),
                str(bundle),
            ],
            check=True,
        )
        if not encrypted_bundle.is_file() or encrypted_bundle.stat().st_size == 0:
            raise RuntimeError("age did not create a non-empty encrypted backup.")

        envelope = {
            "schema_version": 1,
            "created_at": now.isoformat().replace("+00:00", "Z"),
            "artifact": {
                "file": artifact_name,
                "sha256": sha256_file(encrypted_bundle),
                "size_bytes": encrypted_bundle.stat().st_size,
            },
            "encryption": {
                "tool": "age",
                "mode": "recipient",
            },
            "bundle": {
                "format": "tar",
                "backup_file": backup.name,
                "manifest_file": backup_manifest.name,
            },
        }
        artifact_path, envelope_path = _publish_pair(
            encrypted_bundle,
            envelope,
            config.destination_directory,
        )

    removed = apply_retention(
        config.destination_directory,
        keep_daily=config.keep_daily,
        keep_weekly=config.keep_weekly,
    )
    return PublishedBackup(
        artifact_path=artifact_path,
        envelope_path=envelope_path,
        removed_artifacts=removed,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an encrypted RecyclerOS off-platform pilot backup."
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.validate_only:
        validate_runtime(config)
        print("PASS off-platform backup configuration")
        return 0

    result = create_offsite_backup(config)
    print(f"PASS encrypted backup {result.artifact_path.name}")
    print(f"PASS integrity envelope {result.envelope_path.name}")
    print(f"PASS retention removed {len(result.removed_artifacts)} artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
