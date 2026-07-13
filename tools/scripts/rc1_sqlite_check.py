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

    conn.close()
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
