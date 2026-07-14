import os
import re

from pilot_postgres_common import read_secret_setting


def main() -> int:
    target_name = os.getenv("RECYCLEROS_RESTORE_DATABASE_NAME", "")
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", target_name):
        raise RuntimeError("RECYCLEROS_RESTORE_DATABASE_NAME is invalid.")

    import psycopg
    from psycopg import sql

    database_url = read_secret_setting("DATABASE_URL")
    with psycopg.connect(database_url, autocommit=True) as conn, conn.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = %s)",
            (target_name,),
        )
        if cursor.fetchone()[0]:
            raise RuntimeError(f"Restore database already exists: {target_name}")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_name)))

    print(f"PASS created restore database {target_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
