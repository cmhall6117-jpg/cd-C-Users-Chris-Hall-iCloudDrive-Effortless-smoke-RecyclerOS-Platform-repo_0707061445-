import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from pilot_postgres_common import (
    postgres_command_environment,
    read_secret_setting,
    sha256_file,
)


def create_backup(
    output: Path,
    *,
    database_url: str | None = None,
    overwrite: bool = False,
    pg_dump_executable: str = "pg_dump",
) -> Path:
    output = output.resolve()
    if output.exists() and not overwrite:
        raise RuntimeError(f"Backup already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    if database_url is None:
        database_url = read_secret_setting("DATABASE_URL")
    environment, database_name = postgres_command_environment(database_url)
    subprocess.run(
        [
            pg_dump_executable,
            "--format=custom",
            "--no-owner",
            "--no-acl",
            "--file",
            str(output),
        ],
        check=True,
        env=environment,
    )

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("pg_dump did not create a non-empty backup.")
    digest = sha256_file(output)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "database": database_name,
        "file": output.name,
        "sha256": digest,
        "size_bytes": output.stat().st_size,
    }
    manifest_path = output.with_suffix(f"{output.suffix}.manifest.json")
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a RecyclerOS pilot backup.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    output = args.output.resolve()
    manifest_path = create_backup(output, overwrite=args.overwrite)
    print(f"PASS backup {output}")
    print(f"PASS manifest {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
