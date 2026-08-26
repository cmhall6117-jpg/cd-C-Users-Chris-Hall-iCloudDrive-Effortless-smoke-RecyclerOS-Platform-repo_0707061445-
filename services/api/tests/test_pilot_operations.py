from pathlib import Path
import sys

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "tools" / "scripts"
API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(API_DIR))

import pilot_postgres_backup  # noqa: E402
import pilot_postgres_create_database  # noqa: E402
import pilot_postgres_restore  # noqa: E402
import pilot_prepare_secrets  # noqa: E402
import operator_password_rotate  # noqa: E402
import production_bootstrap  # noqa: E402
import production_release_manifest  # noqa: E402
import rc1_postgres_migrate  # noqa: E402
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


def test_restore_rejects_tampered_backup_manifest(tmp_path):
    backup = tmp_path / "pilot.dump"
    manifest = tmp_path / "pilot.dump.manifest.json"
    backup.write_bytes(b"original-backup")
    manifest.write_text(
        """{
  "file": "pilot.dump",
  "size_bytes": 15,
  "sha256": "incorrect"
}
""",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="checksum"):
        pilot_postgres_restore.verify_backup_manifest(backup, manifest)


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


def test_migration_runner_reads_database_url_file(tmp_path):
    database_secret = tmp_path / "database_url"
    database_secret.write_text(DATABASE_URL, encoding="utf-8")

    assert rc1_postgres_migrate._database_url(
        {"DATABASE_URL_FILE": str(database_secret)}
    ) == DATABASE_URL


def test_production_bootstrap_requires_exact_owner_confirmation(
    monkeypatch,
    tmp_path,
):
    database_secret = tmp_path / "database_url"
    password_secret = tmp_path / "owner_password"
    database_secret.write_text(DATABASE_URL, encoding="utf-8")
    password_secret.write_text("production-owner-password", encoding="utf-8")
    monkeypatch.setenv("DATABASE_URL_FILE", str(database_secret))
    monkeypatch.setenv(
        "RECYCLEROS_BOOTSTRAP_OWNER_PASSWORD_FILE",
        str(password_secret),
    )
    monkeypatch.setenv(
        "RECYCLEROS_BOOTSTRAP_OWNER_EMAIL",
        "owner@example.com",
    )
    monkeypatch.setenv("RECYCLEROS_BOOTSTRAP_CONFIRM", "wrong@example.com")

    with pytest.raises(RuntimeError, match="exactly match"):
        production_bootstrap.main()


def test_operator_password_rotation_prompts_without_environment_secret(
    monkeypatch,
    capsys,
):
    captured = {}

    class FakeAuthService:
        def __init__(self, database_url):
            captured["database_url"] = database_url

        def rotate_password(self, *, email, password):
            captured["email"] = email
            captured["password"] = password
            return 3

    password = "new-pilot-operator-password"
    prompts = iter((password, password))
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setattr(
        operator_password_rotate,
        "PostgresAuthService",
        FakeAuthService,
    )
    monkeypatch.setattr(
        operator_password_rotate.getpass,
        "getpass",
        lambda _prompt: next(prompts),
    )

    assert operator_password_rotate.main(
        ["--confirm-email", operator_password_rotate.PILOT_OPERATOR_EMAIL]
    ) == 0
    assert captured == {
        "database_url": DATABASE_URL,
        "email": operator_password_rotate.PILOT_OPERATOR_EMAIL,
        "password": password,
    }
    assert password not in capsys.readouterr().out


def test_operator_password_rotation_rejects_mismatched_confirmation(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setattr(
        operator_password_rotate.getpass,
        "getpass",
        lambda _prompt: pytest.fail("password prompt must not run"),
    )

    with pytest.raises(RuntimeError, match="exactly match"):
        operator_password_rotate.main(
            ["--confirm-email", "another-user@example.com"]
        )


def test_operator_password_rotation_rejects_short_password(monkeypatch):
    prompts = iter(("too-short", "too-short"))
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setattr(
        operator_password_rotate.getpass,
        "getpass",
        lambda _prompt: next(prompts),
    )

    with pytest.raises(RuntimeError, match="at least 24"):
        operator_password_rotate.main(
            ["--confirm-email", operator_password_rotate.PILOT_OPERATOR_EMAIL]
        )


def test_production_release_manifest_pins_image_and_migrations():
    root = Path(__file__).resolve().parents[3]

    manifest = production_release_manifest.build_manifest(
        root=root,
        image="ghcr.io/effortless-smoke/recycleros-api",
        digest="sha256:" + "c" * 64,
        commit="d" * 40,
    )

    assert manifest["image_digest"] == "sha256:" + "c" * 64
    assert manifest["commit"] == "d" * 40
    migration_count = len(
        list((root / "database" / "migrations" / "postgres").glob("*.sql"))
    )
    assert len(manifest["migrations"]) == migration_count
    assert all(len(item["sha256"]) == 64 for item in manifest["migrations"])
