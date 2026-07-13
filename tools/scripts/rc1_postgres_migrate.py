from pathlib import Path
import os
import sys

import psycopg


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is required.")
        return 2

    root = Path(__file__).resolve().parents[2]
    migrations = sorted((root / "database" / "migrations" / "postgres").glob("*.sql"))

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            for migration in migrations:
                cur.execute(migration.read_text(encoding="utf-8"))
                print(f"PASS {migration.name}")
        conn.commit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
