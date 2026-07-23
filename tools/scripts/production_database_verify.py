import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api" / "src"))

from runtime_config import read_config_value  # noqa: E402


def expected_migration_ledger(root: Path = ROOT) -> dict[str, str]:
    migration_directory = root / "database" / "migrations" / "postgres"
    return {
        migration.name: hashlib.sha256(migration.read_bytes()).hexdigest()
        for migration in sorted(migration_directory.glob("*.sql"))
    }


def evaluate_database_snapshot(snapshot: dict, expected_ledger: dict[str, str]) -> dict:
    checks: list[dict] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    record(
        "postgresql_version",
        snapshot["server_version_num"] >= 160000,
        str(snapshot["server_version_num"]),
    )
    record("tls", snapshot["ssl"], "enabled" if snapshot["ssl"] else "disabled")
    role_is_limited = not any(
        snapshot[name]
        for name in ("rolsuper", "rolcreatedb", "rolcreaterole", "rolreplication")
    )
    record(
        "least_privilege_role",
        role_is_limited,
        "limited" if role_is_limited else "privileged",
    )
    record(
        "timezone",
        snapshot["timezone"] in {"UTC", "Etc/UTC"},
        snapshot["timezone"],
    )
    record("schema_readiness", snapshot["schema_ready"], "required tables")
    record("active_membership", snapshot["active_membership"], "active tenant owner")

    actual_ledger = snapshot["migration_ledger"]
    record(
        "migration_ledger",
        actual_ledger == expected_ledger,
        f"{len(actual_ledger)} of {len(expected_ledger)} expected migrations",
    )
    return {
        "schema_version": 1,
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
    }


def read_database_snapshot(database_url: str) -> dict:
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError(
            "Database verification requires services/api/requirements-postgres.txt"
        ) from exc

    with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
        cursor.execute("SHOW server_version_num")
        server_version_num = int(cursor.fetchone()[0])
        cursor.execute(
            "SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()"
        )
        ssl_enabled = bool(cursor.fetchone()[0])
        cursor.execute(
            """
            SELECT rolsuper, rolcreatedb, rolcreaterole, rolreplication
            FROM pg_roles
            WHERE rolname = current_user
            """
        )
        role = cursor.fetchone()
        cursor.execute("SELECT current_setting('TimeZone')")
        timezone_name = cursor.fetchone()[0]
        cursor.execute(
            """
            SELECT
                to_regclass('public.organizations') IS NOT NULL
                AND to_regclass('public.workspaces') IS NOT NULL
                AND to_regclass('public.auth_users') IS NOT NULL
                AND to_regclass('public.auth_tenant_memberships') IS NOT NULL
                AND to_regclass('public.opportunities') IS NOT NULL
                AND to_regclass('public.inventory_items') IS NOT NULL
                AND to_regclass('public.recycleros_schema_migrations') IS NOT NULL
            """
        )
        schema_ready = bool(cursor.fetchone()[0])

        active_membership = False
        migration_ledger: dict[str, str] = {}
        if schema_ready:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM auth_users auth_user
                    JOIN auth_tenant_memberships membership
                      ON membership.user_id = auth_user.id
                    WHERE auth_user.active = true
                      AND membership.role IN ('owner', 'admin')
                )
                """
            )
            active_membership = bool(cursor.fetchone()[0])
            cursor.execute(
                "SELECT filename, sha256 FROM recycleros_schema_migrations"
            )
            migration_ledger = dict(cursor.fetchall())

    return {
        "server_version_num": server_version_num,
        "ssl": ssl_enabled,
        "rolsuper": role[0],
        "rolcreatedb": role[1],
        "rolcreaterole": role[2],
        "rolreplication": role[3],
        "timezone": timezone_name,
        "schema_ready": schema_ready,
        "active_membership": active_membership,
        "migration_ledger": migration_ledger,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify RecyclerOS managed PostgreSQL production controls."
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    database_url = read_config_value("DATABASE_URL", required=True)
    snapshot = read_database_snapshot(database_url)
    report = evaluate_database_snapshot(snapshot, expected_migration_ledger())
    serialized = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
