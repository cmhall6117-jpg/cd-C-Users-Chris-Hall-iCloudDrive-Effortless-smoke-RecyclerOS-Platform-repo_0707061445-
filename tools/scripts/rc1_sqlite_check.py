from pathlib import Path
import sqlite3
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    artifacts = root / "build_artifacts"
    artifacts.mkdir(exist_ok=True)
    db_path = artifacts / "rc1_clean.sqlite"
    report_path = artifacts / "sqlite_init_report.txt"

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    lines: list[str] = []
    ok = True

    for path in sorted((root / "database/migrations/sqlite").glob("*.sql")):
        sql = path.read_text(encoding="utf-8")
        try:
            conn.executescript(sql)
            lines.append(f"PASS {path.name}")
        except Exception as exc:
            ok = False
            lines.append(f"FAIL {path.name}: {type(exc).__name__}: {exc}")
            break

    if ok:
        tables = [
            row[0]
            for row in conn.execute(
                "select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name"
            )
        ]
        lines.append("TABLES " + ", ".join(tables))
        tenant_tables = [
            "vehicles",
            "opportunities",
            "business_events",
            "sync_queue",
            "vehicle_timeline",
            "procurement_analyses",
            "procurement_scenarios",
            "pick_list_items",
            "harvest_sessions",
            "harvested_parts",
            "storage_locations",
            "inventory_items",
            "integration_smoke_test_runs",
            "integration_issues",
        ]
        for table in tenant_tables:
            columns = {row[1] for row in conn.execute(f"pragma table_info({table})")}
            missing = {"organization_id", "workspace_id"} - columns
            if missing:
                ok = False
                lines.append(f"FAIL {table}: missing tenant columns {', '.join(sorted(missing))}")
        if ok:
            lines.append("PASS tenant columns present")
        try:
            conn.execute(
                """
                insert into vehicles (
                    id, vehicle_code, created_at, organization_id, workspace_id
                ) values (
                    'veh-bad-tenant', 'VEH-BAD-TENANT', datetime('now'), 'org-local', 'workspace-missing'
                )
                """
            )
            ok = False
            lines.append("FAIL tenant mismatch trigger did not reject invalid vehicle workspace")
        except sqlite3.IntegrityError:
            lines.append("PASS tenant mismatch rejected")

    conn.close()
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
