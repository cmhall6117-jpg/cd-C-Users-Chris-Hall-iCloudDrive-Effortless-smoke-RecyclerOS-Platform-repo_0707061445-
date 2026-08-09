import ipaddress
import os
from pathlib import Path
import re
import sys

from runtime_config import read_config_value


def _positive_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value < 1:
        raise RuntimeError(f"{name} must be at least 1.")
    return value


def build_command(root: Path | None = None) -> list[str]:
    if os.getenv("RECYCLEROS_DEPLOYMENT_MODE", "").casefold() != "production":
        raise RuntimeError("The production entrypoint requires production mode.")
    read_config_value("DATABASE_URL", required=True)

    release_sha = os.getenv("RECYCLEROS_RELEASE_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", release_sha):
        raise RuntimeError("RECYCLEROS_RELEASE_SHA must be a 40-character Git SHA.")

    forwarded_allow_ips = os.getenv("RECYCLEROS_FORWARDED_ALLOW_IPS", "").strip()
    if not forwarded_allow_ips or "*" in forwarded_allow_ips:
        raise RuntimeError(
            "RECYCLEROS_FORWARDED_ALLOW_IPS must explicitly list trusted proxies."
        )
    try:
        for address in forwarded_allow_ips.split(","):
            ipaddress.ip_network(address.strip(), strict=False)
    except ValueError as exc:
        raise RuntimeError(
            "RECYCLEROS_FORWARDED_ALLOW_IPS contains an invalid IP or network."
        ) from exc

    application_root = root or Path(__file__).resolve().parents[2]
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--app-dir",
        str(application_root / "services" / "api" / "src"),
        "--host",
        "0.0.0.0",
        "--port",
        str(_positive_int("PORT", 8000)),
        "--workers",
        str(_positive_int("RECYCLEROS_API_WORKERS", 2)),
        "--proxy-headers",
        "--forwarded-allow-ips",
        forwarded_allow_ips,
        "--timeout-keep-alive",
        "5",
    ]


def main() -> int:
    os.execvpe(sys.executable, build_command(), os.environ.copy())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
