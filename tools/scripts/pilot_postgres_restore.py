import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from pilot_postgres_common import (
    postgres_command_environment,
    read_secret_setting,
)


def verify_backup_manifest(backup: Path, manifest_path: Path) -> None:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Unable to read the backup manifest.") from exc

    actual_digest = hashlib.sha256(backup.read_bytes()).hexdigest()
    if manifest.get("file") != backup.name:
        raise RuntimeError("Backup manifest filename does not match the backup.")
    if manifest.get("size_bytes") != backup.stat().st_size:
        raise RuntimeError("Backup manifest size does not match the backup.")
    if manifest.get("sha256") != actual_digest:
        raise RuntimeError("Backup manifest checksum does not match the backup.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore a RecyclerOS pilot backup.")
    parser.add_argument("--backup", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    backup = args.backup.resolve()
    if not backup.is_file():
        raise RuntimeError(f"Backup does not exist: {backup}")
    if args.manifest is not None:
        verify_backup_manifest(backup, args.manifest.resolve())

    database_url = read_secret_setting("RECYCLEROS_RESTORE_DATABASE_URL")
    environment, database_name = postgres_command_environment(database_url)
    if os.getenv("RECYCLEROS_RESTORE_CONFIRM") != database_name:
        raise RuntimeError(
            "RECYCLEROS_RESTORE_CONFIRM must exactly match the target database name."
        )

    subprocess.run(
        [
            "pg_restore",
            "--clean",
            "--if-exists",
            "--exit-on-error",
            "--no-owner",
            "--no-acl",
            "--dbname",
            database_name,
            str(backup),
        ],
        check=True,
        env=environment,
    )
    print(f"PASS restore {database_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
