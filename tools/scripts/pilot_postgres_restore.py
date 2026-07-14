import argparse
import os
from pathlib import Path
import subprocess

from pilot_postgres_common import (
    postgres_command_environment,
    read_secret_setting,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore a RecyclerOS pilot backup.")
    parser.add_argument("--backup", required=True, type=Path)
    args = parser.parse_args()

    backup = args.backup.resolve()
    if not backup.is_file():
        raise RuntimeError(f"Backup does not exist: {backup}")

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
