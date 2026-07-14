from pathlib import Path
import sys

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "tools" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import pilot_postgres_backup  # noqa: E402
import pilot_postgres_create_database  # noqa: E402
import pilot_postgres_restore  # noqa: E402
import pilot_prepare_secrets  # noqa: E402
from pilot_postgres_common import postgres_command_environment  # noqa: E402


DATABASE_URL = "postgresql://pilot_user:secret_value@db.example:5433/pilot_db"


def test_postgres_command_environment_keeps_password_out_of_database_name():
    environment, database_name = postgres_command_environment(
        DATABASE_URL,
        environ={"PATH": "test-path"},
    )

    assert database_name == "pilot_db"
    assert environment["PGHOST"] == "db.example"
    assert environment["PGPORT"] == "5433"
    assert environment["PGPASSWORD"] == "secret_value"


def test_backup_command_does_not_include_database_secret(
    monkeypatch,
    tmp_path,
):
    output = tmp_path / "pilot.dump"
    captured_command = []

    def fake_run(command, **kwargs):
        captured_command.extend(command)
        Path(command[command.index("--file") + 1]).write_bytes(b"pilot-backup")

    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setattr(pilot_postgres_backup.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        ["pilot_postgres_backup.py", "--output", str(output)],
    )

    assert pilot_postgres_backup.main() == 0
    assert "secret_value" not in " ".join(captured_command)
    assert output.with_suffix(".dump.manifest.json").is_file()


def test_restore_requires_exact_target_confirmation(monkeypatch, tmp_path):
    backup = tmp_path / "pilot.dump"
    backup.write_bytes(b"pilot-backup")
    monkeypatch.setenv("RECYCLEROS_RESTORE_DATABASE_URL", DATABASE_URL)
    monkeypatch.setenv("RECYCLEROS_RESTORE_CONFIRM", "wrong_database")
    monkeypatch.setattr(
        sys,
        "argv",
        ["pilot_postgres_restore.py", "--backup", str(backup)],
    )

    with pytest.raises(RuntimeError, match="exactly match"):
        pilot_postgres_restore.main()


def test_restore_database_name_is_strictly_validated(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setenv("RECYCLEROS_RESTORE_DATABASE_NAME", "unsafe-name;drop")

    with pytest.raises(RuntimeError, match="invalid"):
        pilot_postgres_create_database.main()


def test_secret_preparation_does_not_overwrite(tmp_path):
    paths = pilot_prepare_secrets.prepare_secrets(tmp_path)

    assert {path.name for path in paths} == {
        "database_url",
        "operator_password",
        "postgres_password",
    }
    assert "@postgres:5432/recycleros_pilot" in (
        tmp_path / "database_url"
    ).read_text(encoding="utf-8")
    with pytest.raises(RuntimeError, match="Refusing to overwrite"):
        pilot_prepare_secrets.prepare_secrets(tmp_path)
