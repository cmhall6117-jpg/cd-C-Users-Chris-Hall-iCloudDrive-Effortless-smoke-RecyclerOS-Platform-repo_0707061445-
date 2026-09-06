from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, replace
import os
import queue
import re
import shutil
import signal
import subprocess
import threading
import time
from typing import Any, Callable, Iterator, TextIO
from urllib.parse import urlsplit


_ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_TUNNEL_URL = re.compile(r"^\s*URL:\s*(postgres(?:ql)?://\S+)\s*$")


@dataclass(frozen=True)
class RailwayTunnelSettings:
    railway_executable: str
    ssh_executable: str
    project_id: str
    environment: str
    service: str
    local_port: int
    startup_timeout_seconds: int


def resolve_railway_tunnel_tools(
    settings: RailwayTunnelSettings,
) -> RailwayTunnelSettings:
    railway_executable = shutil.which(settings.railway_executable)
    if railway_executable is None:
        raise RuntimeError("The configured Railway executable is not available.")
    ssh_executable = shutil.which(settings.ssh_executable)
    if ssh_executable is None:
        raise RuntimeError("The configured SSH executable is not available.")
    return replace(
        settings,
        railway_executable=railway_executable,
        ssh_executable=ssh_executable,
    )


def _read_process_lines(stream: TextIO, lines: queue.Queue[str | None]) -> None:
    try:
        for line in iter(stream.readline, ""):
            lines.put(line)
    finally:
        lines.put(None)


def _validated_tunnel_url(raw_url: str, expected_port: int) -> str:
    try:
        parsed = urlsplit(raw_url)
        port = parsed.port
    except ValueError as exc:
        raise RuntimeError("Railway returned an invalid tunnel URL.") from exc
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise RuntimeError("Railway tunnel did not return a PostgreSQL URL.")
    if parsed.hostname != "127.0.0.1" or port != expected_port:
        raise RuntimeError("Railway tunnel URL does not match the requested loopback port.")
    if not parsed.username or parsed.password is None or not parsed.path.strip("/"):
        raise RuntimeError("Railway tunnel URL is missing required connection fields.")
    return raw_url


def _stop_process(
    process: subprocess.Popen[str],
    *,
    windows: bool | None = None,
    tree_killer: Callable[..., Any] = subprocess.run,
) -> None:
    if process.poll() is not None:
        return
    windows = os.name == "nt" if windows is None else windows
    if windows:
        try:
            tree_killer(
                [
                    "taskkill",
                    "/PID",
                    str(process.pid),
                    "/T",
                    "/F",
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            process.wait(timeout=10)
            if process.poll() is not None:
                return
        except (OSError, subprocess.TimeoutExpired):
            pass
    try:
        if windows:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            process.send_signal(signal.SIGINT)
        process.wait(timeout=10)
        return
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        process.terminate()
        process.wait(timeout=5)
        return
    except (OSError, subprocess.TimeoutExpired):
        pass
    process.kill()
    process.wait(timeout=5)


@contextmanager
def open_railway_postgres_tunnel(
    settings: RailwayTunnelSettings,
    *,
    popen_factory: Callable[..., subprocess.Popen[str]] = subprocess.Popen,
    tree_killer: Callable[..., Any] = subprocess.run,
) -> Iterator[str]:
    settings = resolve_railway_tunnel_tools(settings)
    command = [
        settings.railway_executable,
        "connect",
        settings.service,
        "--tunnel-only",
        "--project",
        settings.project_id,
        "--environment",
        settings.environment,
        "--port",
        str(settings.local_port),
    ]
    environment = os.environ.copy()
    ssh_directory = os.path.dirname(settings.ssh_executable)
    environment["PATH"] = os.pathsep.join(
        item
        for item in (ssh_directory, environment.get("PATH", ""))
        if item
    )
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    process = popen_factory(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env=environment,
        creationflags=creationflags,
    )
    if process.stdout is None:
        _stop_process(process, tree_killer=tree_killer)
        raise RuntimeError("Unable to capture Railway tunnel readiness.")

    lines: queue.Queue[str | None] = queue.Queue()
    reader = threading.Thread(
        target=_read_process_lines,
        args=(process.stdout, lines),
        daemon=True,
    )
    reader.start()
    deadline = time.monotonic() + settings.startup_timeout_seconds
    tunnel_url = None
    try:
        while tunnel_url is None:
            if process.poll() is not None and lines.empty():
                raise RuntimeError(
                    "Railway SSH tunnel exited before it became ready. "
                    "Verify Railway authentication and SSH-key registration."
                )
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("Timed out waiting for the Railway SSH tunnel.")
            try:
                line = lines.get(timeout=min(0.25, remaining))
            except queue.Empty:
                continue
            if line is None:
                if process.poll() is not None:
                    raise RuntimeError(
                        "Railway SSH tunnel exited before it became ready. "
                        "Verify Railway authentication and SSH-key registration."
                    )
                continue
            clean_line = _ANSI_ESCAPE.sub("", line)
            match = _TUNNEL_URL.fullmatch(clean_line.rstrip("\r\n"))
            if match is not None:
                tunnel_url = _validated_tunnel_url(
                    match.group(1),
                    settings.local_port,
                )

        yield tunnel_url
    finally:
        _stop_process(process, tree_killer=tree_killer)
        reader.join(timeout=2)
