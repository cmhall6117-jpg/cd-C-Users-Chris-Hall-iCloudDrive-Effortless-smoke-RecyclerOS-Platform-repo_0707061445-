from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "tools" / "scripts"
API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(API_DIR))

import pilot_postgres_backup  # noqa: E402
import pilot_postgres_create_database  # noqa: E402
import pilot_postgres_offsite_backup  # noqa: E402
import pilot_postgres_restore  # noqa: E402
import pilot_prepare_secrets  # noqa: E402
import operator_password_rotate  # noqa: E402
import production_bootstrap  # noqa: E402
import production_release_manifest  # noqa: E402
import rc1_postgres_migrate  # noqa: E402
from pilot_postgres_common import postgres_command_environment  # noqa: E402


DATABASE_URL = "postgresql://pilot_user:secret_value@db.example:5433/pilot_db"


def _offsite_config(
    tmp_path,
    monkeypatch,
    *,
    recipient="age1testrecipient",
    keep_daily=14,
    keep_weekly=8,
):
    destination = tmp_path / "destination"
    staging = tmp_path / "staging"
    destination.mkdir()
    staging.mkdir()
    database_url_file = tmp_path / "database_url"
    recipient_file = tmp_path / "recipient"
    database_url_file.write_text(DATABASE_URL, encoding="utf-8")
    recipient_file.write_text(recipient, encoding="utf-8")
    config_path = tmp_path / "offsite-backup.json"
    config_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "database_url_file": str(database_url_file),
                "destination_directory": str(destination),
                "age_recipient_file": str(recipient_file),
                "staging_directory": str(staging),
                "age_executable": "age",
                "pg_dump_executable": "pg_dump",
                "keep_daily": keep_daily,
                "keep_weekly": keep_weekly,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        pilot_postgres_offsite_backup.shutil,
        "which",
        lambda executable: executable,
    )
    return pilot_postgres_offsite_backup.load_config(
        config_path,
        repository_root=tmp_path / "repository",
    )


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


def test_offsite_backup_publishes_only_ciphertext_and_envelope(
    monkeypatch,
    tmp_path,
):
    config = _offsite_config(tmp_path, monkeypatch)
    captured_command = []

    def fake_backup(output, *, database_url, pg_dump_executable):
        assert database_url == DATABASE_URL
        assert pg_dump_executable == "pg_dump"
        output.write_bytes(b"plaintext-pilot-backup")
        manifest = output.with_suffix(f"{output.suffix}.manifest.json")
        manifest.write_text('{"sha256": "plaintext-digest"}\n', encoding="utf-8")
        return manifest

    def fake_age(command, *, check):
        assert check is True
        captured_command.extend(command)
        encrypted_output = Path(command[command.index("--output") + 1])
        encrypted_output.write_bytes(b"age-encrypted-pilot-backup")

    result = pilot_postgres_offsite_backup.create_offsite_backup(
        config,
        now=datetime(2026, 8, 29, 12, 30, tzinfo=timezone.utc),
        artifact_id="0123abcd",
        age_runner=fake_age,
        backup_creator=fake_backup,
    )

    assert result.artifact_path.read_bytes() == b"age-encrypted-pilot-backup"
    assert result.envelope_path.is_file()
    assert sorted(path.name for path in config.destination_directory.iterdir()) == [
        "recycleros-pilot-20260829T123000Z-0123abcd.tar.age",
        "recycleros-pilot-20260829T123000Z-0123abcd.tar.age.envelope.json",
    ]
    envelope = json.loads(result.envelope_path.read_text(encoding="utf-8"))
    assert envelope["encryption"] == {"tool": "age", "mode": "recipient"}
    assert envelope["artifact"]["size_bytes"] == 26
    assert "secret_value" not in " ".join(captured_command)
    assert DATABASE_URL not in result.envelope_path.read_text(encoding="utf-8")
    assert list(config.staging_directory.iterdir()) == []


def test_offsite_backup_encryption_failure_leaves_no_plaintext_or_destination_file(
    monkeypatch,
    tmp_path,
):
    config = _offsite_config(tmp_path, monkeypatch)

    def fake_backup(output, *, database_url, pg_dump_executable):
        output.write_bytes(b"plaintext-pilot-backup")
        manifest = output.with_suffix(f"{output.suffix}.manifest.json")
        manifest.write_text("{}\n", encoding="utf-8")
        return manifest

    def fail_age(_command, *, check):
        raise RuntimeError("simulated age failure")

    with pytest.raises(RuntimeError, match="simulated age failure"):
        pilot_postgres_offsite_backup.create_offsite_backup(
            config,
            age_runner=fail_age,
            backup_creator=fake_backup,
        )

    assert list(config.destination_directory.iterdir()) == []
    assert list(config.staging_directory.iterdir()) == []


def test_offsite_backup_copy_checksum_failure_removes_destination_pair(
    monkeypatch,
    tmp_path,
):
    config = _offsite_config(tmp_path, monkeypatch)

    def fake_backup(output, *, database_url, pg_dump_executable):
        output.write_bytes(b"plaintext-pilot-backup")
        manifest = output.with_suffix(f"{output.suffix}.manifest.json")
        manifest.write_text("{}\n", encoding="utf-8")
        return manifest

    def fake_age(command, *, check):
        encrypted_output = Path(command[command.index("--output") + 1])
        encrypted_output.write_bytes(b"expected-ciphertext")

    def corrupt_copy(_source, destination):
        destination.write_bytes(b"corrupted-ciphertext")

    monkeypatch.setattr(
        pilot_postgres_offsite_backup,
        "_copy_exclusive",
        corrupt_copy,
    )

    with pytest.raises(RuntimeError, match="checksum mismatch"):
        pilot_postgres_offsite_backup.create_offsite_backup(
            config,
            age_runner=fake_age,
            backup_creator=fake_backup,
        )

    assert list(config.destination_directory.iterdir()) == []
    assert list(config.staging_directory.iterdir()) == []


def test_offsite_backup_rejects_private_age_identity(monkeypatch, tmp_path):
    config = _offsite_config(
        tmp_path,
        monkeypatch,
        recipient="AGE-SECRET-KEY-1TEST",
    )

    with pytest.raises(RuntimeError, match="private identity"):
        pilot_postgres_offsite_backup.validate_runtime(config)


def test_offsite_backup_config_must_be_outside_repository(tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()
    config_path = repository / "offsite-backup.json"
    config_path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="outside the Git repository"):
        pilot_postgres_offsite_backup.load_config(
            config_path,
            repository_root=repository,
        )


def test_offsite_retention_keeps_daily_and_older_weekly_boundaries(tmp_path):
    destination = tmp_path / "destination"
    destination.mkdir()

    def write_record(created_at, identifier):
        timestamp = created_at.strftime("%Y%m%dT%H%M%SZ")
        artifact_name = (
            f"recycleros-pilot-{timestamp}-{identifier}.tar.age"
        )
        artifact = destination / artifact_name
        artifact.write_bytes(b"ciphertext")
        envelope = destination / f"{artifact_name}.envelope.json"
        envelope.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "created_at": created_at.isoformat().replace("+00:00", "Z"),
                    "artifact": {
                        "file": artifact_name,
                        "sha256": "0" * 64,
                        "size_bytes": artifact.stat().st_size,
                    },
                    "encryption": {
                        "tool": "age",
                        "mode": "recipient",
                    },
                    "bundle": {"format": "tar"},
                }
            ),
            encoding="utf-8",
        )
        return artifact, envelope

    records = [
        write_record(datetime(2026, 8, 29, tzinfo=timezone.utc), "00000001"),
        write_record(datetime(2026, 8, 28, tzinfo=timezone.utc), "00000002"),
        write_record(datetime(2026, 8, 20, tzinfo=timezone.utc), "00000003"),
        write_record(datetime(2026, 8, 19, tzinfo=timezone.utc), "00000004"),
        write_record(datetime(2026, 8, 10, tzinfo=timezone.utc), "00000005"),
    ]
    unrelated = destination / "operator-notes.txt"
    unrelated.write_text("retain me", encoding="utf-8")
    invalid_artifact = destination / (
        "recycleros-pilot-20260801T000000Z-ffffffff.tar.age"
    )
    invalid_artifact.write_bytes(b"ciphertext")
    invalid_envelope = destination / f"{invalid_artifact.name}.envelope.json"
    invalid_envelope.write_text("not-json", encoding="utf-8")

    removed = pilot_postgres_offsite_backup.apply_retention(
        destination,
        keep_daily=2,
        keep_weekly=1,
    )

    assert set(removed) == {records[3][0].name, records[4][0].name}
    assert all(path.is_file() for pair in records[:3] for path in pair)
    assert all(not path.exists() for pair in records[3:] for path in pair)
    assert unrelated.is_file()
    assert invalid_artifact.is_file()
    assert invalid_envelope.is_file()


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
