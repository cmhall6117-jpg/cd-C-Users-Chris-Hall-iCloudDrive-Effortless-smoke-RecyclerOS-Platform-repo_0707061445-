import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from pilot_postgres_common import (
    postgres_command_environment,
    read_secret_setting,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a RecyclerOS pilot backup.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists() and not args.overwrite:
        raise RuntimeError(f"Backup already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    database_url = read_secret_setting("DATABASE_URL")
    environment, database_name = postgres_command_environment(database_url)
    subprocess.run(
        [
            "pg_dump",
            "--format=custom",
            "--no-owner",
            "--no-acl",
            "--file",
            str(output),
        ],
        check=True,
        env=environment,
    )

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
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
    print(f"PASS backup {output}")
    print(f"PASS manifest {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
