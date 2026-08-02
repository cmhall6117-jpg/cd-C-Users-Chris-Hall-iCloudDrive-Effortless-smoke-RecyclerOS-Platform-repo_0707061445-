from pathlib import Path
import hashlib
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api" / "src"))

from runtime_config import read_config_value  # noqa: E402


def _database_url(environ=None) -> str:
    value = read_config_value(
        "DATABASE_URL",
        required=True,
        environ=os.environ if environ is None else environ,
    )
    return value


def main() -> int:
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError(
            "PostgreSQL migrations require services/api/requirements-postgres.txt"
        ) from exc

    database_url = _database_url()
    migrations = sorted((ROOT / "database" / "migrations" / "postgres").glob("*.sql"))

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pg_advisory_xact_lock(hashtext('recycleros-schema-migrations'))"
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS recycleros_schema_migrations (
                    filename TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL CHECK (length(sha256) = 64),
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            for migration in migrations:
                sql = migration.read_text(encoding="utf-8")
                digest = hashlib.sha256(sql.encode("utf-8")).hexdigest()
                cur.execute(
                    """
                    SELECT sha256
                    FROM recycleros_schema_migrations
                    WHERE filename = %s
                    """,
                    (migration.name,),
                )
                existing = cur.fetchone()
                if existing is not None:
                    if existing[0] != digest:
                        raise RuntimeError(
                            f"Migration checksum mismatch: {migration.name}"
                        )
                    print(f"SKIP {migration.name}")
                    continue

                cur.execute(sql)
                cur.execute(
                    """
                    INSERT INTO recycleros_schema_migrations (filename, sha256)
                    VALUES (%s, %s)
                    """,
                    (migration.name, digest),
                )
                print(f"PASS {migration.name}")
        conn.commit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
