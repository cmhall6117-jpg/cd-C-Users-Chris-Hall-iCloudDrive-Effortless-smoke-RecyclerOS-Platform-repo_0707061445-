import os
from pathlib import Path
import subprocess
import sys

from runtime_config import read_config_value


def _positive_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value < 1:
        raise RuntimeError(f"{name} must be at least 1.")
    return value


def main() -> int:
    database_url = read_config_value("DATABASE_URL", required=True)
    runtime_environment = os.environ.copy()
    migration_environment = runtime_environment.copy()
    migration_environment.pop("DATABASE_URL_FILE", None)
    migration_environment["DATABASE_URL"] = database_url

    root = Path(__file__).resolve().parents[2]
    subprocess.run(
        [
            sys.executable,
            str(root / "tools" / "scripts" / "rc1_postgres_migrate.py"),
        ],
        check=True,
        env=migration_environment,
    )

    port = _positive_int("PORT", 8000)
    workers = _positive_int("RECYCLEROS_API_WORKERS", 1)
    forwarded_allow_ips = os.getenv(
        "RECYCLEROS_FORWARDED_ALLOW_IPS",
        "127.0.0.1",
    )
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--app-dir",
        str(root / "services" / "api" / "src"),
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
        "--workers",
        str(workers),
        "--proxy-headers",
        "--forwarded-allow-ips",
        forwarded_allow_ips,
    ]
    os.execvpe(sys.executable, command, runtime_environment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
