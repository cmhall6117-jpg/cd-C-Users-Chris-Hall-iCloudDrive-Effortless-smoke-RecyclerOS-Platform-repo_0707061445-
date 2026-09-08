import io
from pathlib import Path
import signal
import sys

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "tools" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import pilot_railway_tunnel  # noqa: E402


class FakeProcess:
    def __init__(self, output, *, returncode=None):
        self.stdout = io.StringIO(output)
        self.returncode = returncode
        self.signals = []
        self.pid = 4242

    def poll(self):
        return self.returncode

    def send_signal(self, value):
        self.signals.append(value)
        self.returncode = 0

    def wait(self, timeout=None):
        return self.returncode

    def terminate(self):
        self.returncode = 0

    def kill(self):
        self.returncode = 0


def _settings():
    return pilot_railway_tunnel.RailwayTunnelSettings(
        railway_executable="railway",
        ssh_executable="ssh",
        project_id="22bdb278-c849-4c65-bd93-0031053344a1",
        environment="pilot",
        service="Postgres",
        local_port=15432,
        startup_timeout_seconds=10,
    )


def test_railway_tunnel_keeps_credentials_out_of_process_arguments(monkeypatch):
    monkeypatch.setattr(
        pilot_railway_tunnel.shutil,
        "which",
        lambda executable: executable,
    )
    process = FakeProcess(
        "PostgreSQL tunnel open\n"
        "  Password: secret_value\n"
        "  URL:      postgresql://pilot_user:secret_value@127.0.0.1:15432/pilot_db\n"
    )
    captured = {}
    tree_kill_commands = []

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return process

    def fake_tree_killer(command, **_kwargs):
        tree_kill_commands.append(command)
        process.returncode = 0

    with pilot_railway_tunnel.open_railway_postgres_tunnel(
        _settings(),
        popen_factory=fake_popen,
        tree_killer=fake_tree_killer,
    ) as database_url:
        assert database_url.endswith("@127.0.0.1:15432/pilot_db")

    command_text = " ".join(captured["command"])
    assert "secret_value" not in command_text
    assert captured["command"][-2:] == ["--port", "15432"]
    assert captured["kwargs"]["stdin"] is pilot_railway_tunnel.subprocess.DEVNULL
    if pilot_railway_tunnel.os.name == "nt":
        assert tree_kill_commands == [
            ["taskkill", "/PID", "4242", "/T", "/F"]
        ]
        assert process.signals == []
    else:
        assert tree_kill_commands == []
        assert process.signals == [signal.SIGINT]


def test_railway_tunnel_rejects_non_loopback_connection(monkeypatch):
    monkeypatch.setattr(
        pilot_railway_tunnel.shutil,
        "which",
        lambda executable: executable,
    )
    process = FakeProcess(
        "  URL:      postgresql://pilot_user:secret_value@db.example:15432/pilot_db\n"
    )

    def fake_tree_killer(_command, **_kwargs):
        process.returncode = 0

    with pytest.raises(RuntimeError, match="requested loopback port"):
        with pilot_railway_tunnel.open_railway_postgres_tunnel(
            _settings(),
            popen_factory=lambda *_args, **_kwargs: process,
            tree_killer=fake_tree_killer,
        ):
            pytest.fail("unsafe tunnel URL must not be yielded")


def test_railway_tunnel_failure_does_not_echo_credentials(monkeypatch):
    monkeypatch.setattr(
        pilot_railway_tunnel.shutil,
        "which",
        lambda executable: executable,
    )
    process = FakeProcess("Password: secret_value\n", returncode=1)

    with pytest.raises(RuntimeError) as exc_info:
        with pilot_railway_tunnel.open_railway_postgres_tunnel(
            _settings(),
            popen_factory=lambda *_args, **_kwargs: process,
        ):
            pytest.fail("failed tunnel must not be yielded")

    assert "secret_value" not in str(exc_info.value)


def test_windows_tunnel_cleanup_kills_the_full_process_tree():
    process = FakeProcess("", returncode=None)
    commands = []

    def fake_tree_killer(command, **kwargs):
        commands.append((command, kwargs))
        process.returncode = 0

    pilot_railway_tunnel._stop_process(
        process,
        windows=True,
        tree_killer=fake_tree_killer,
    )

    assert commands[0][0] == ["taskkill", "/PID", "4242", "/T", "/F"]
    assert commands[0][1]["check"] is False
    assert process.signals == []
