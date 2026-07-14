import argparse
import os

from pilot_postgres_common import read_secret_setting


REQUIRED_TABLES = (
    "auth_sessions",
    "auth_tenant_memberships",
    "auth_users",
    "harvest_sessions",
    "inventory_items",
    "opportunities",
    "pick_list_items",
    "rc1_code_sequences",
    "vehicles",
)


def main() -> int:
    import psycopg

    parser = argparse.ArgumentParser(description="Verify a RecyclerOS pilot database.")
    parser.add_argument("--require-runtime-data", action="store_true")
    args = parser.parse_args()

    variable = os.getenv("RECYCLEROS_VERIFY_DATABASE_VARIABLE", "DATABASE_URL")
    database_url = read_secret_setting(variable)
    with psycopg.connect(database_url) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
        )
        present = {row[0] for row in cursor.fetchall()}
        missing = sorted(set(REQUIRED_TABLES) - present)
        if missing:
            raise RuntimeError(f"Missing required tables: {', '.join(missing)}")

        cursor.execute(
            "SELECT prefix FROM rc1_code_sequences ORDER BY prefix"
        )
        if [row[0] for row in cursor.fetchall()] != ["INV", "OPP", "VEH"]:
            raise RuntimeError("RC1 code sequences are incomplete.")

        if args.require_runtime_data:
            for table in ("auth_users", "opportunities", "inventory_items"):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                if cursor.fetchone()[0] < 1:
                    raise RuntimeError(f"Expected restored runtime data in {table}.")

    print("PASS pilot database verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
