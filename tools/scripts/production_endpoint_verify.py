import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import socket
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


def validate_base_url(base_url: str) -> tuple[str, int]:
    parsed = urlsplit(base_url)
    try:
        port = parsed.port or 443
    except ValueError as exc:
        raise RuntimeError("Production API URL has an invalid port.") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError("Production API URL must be an exact HTTPS origin.")
    return parsed.hostname, port


def fetch_endpoint(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            return {
                "status": response.status,
                "headers": {key.casefold(): value for key, value in response.headers.items()},
                "json": json.loads(body) if body else None,
            }
    except HTTPError as exc:
        return {
            "status": exc.code,
            "headers": {key.casefold(): value for key, value in exc.headers.items()},
            "json": None,
        }
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Unable to reach the production API endpoint.") from exc


def probe_tls(hostname: str, port: int) -> dict:
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=10) as connection:
            with context.wrap_socket(connection, server_hostname=hostname) as secured:
                certificate = secured.getpeercert()
                expires_at = datetime.fromtimestamp(
                    ssl.cert_time_to_seconds(certificate["notAfter"]),
                    tz=timezone.utc,
                )
                days_remaining = int(
                    (expires_at - datetime.now(timezone.utc)).total_seconds() // 86400
                )
                return {
                    "protocol": secured.version(),
                    "days_remaining": days_remaining,
                }
    except (OSError, ssl.SSLError, KeyError) as exc:
        raise RuntimeError("TLS certificate verification failed.") from exc


def evaluate_endpoint(
    *,
    base_url: str,
    release_sha: str,
    minimum_certificate_days: int,
    fetcher=fetch_endpoint,
    tls_prober=probe_tls,
) -> dict:
    hostname, port = validate_base_url(base_url)
    if not re.fullmatch(r"[0-9a-f]{40}", release_sha):
        raise RuntimeError("Release SHA must be a complete 40-character Git SHA.")
    if minimum_certificate_days < 1:
        raise RuntimeError("Minimum certificate days must be at least 1.")

    checks: list[dict] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    tls = tls_prober(hostname, port)
    record(
        "tls_certificate",
        tls["days_remaining"] >= minimum_certificate_days,
        f"{tls['protocol']}; {tls['days_remaining']} days remaining",
    )
    record(
        "tls_protocol",
        tls["protocol"] in {"TLSv1.2", "TLSv1.3"},
        tls["protocol"],
    )

    live = fetcher(urljoin(f"{base_url}/", "v1/health/live"))
    ready = fetcher(urljoin(f"{base_url}/", "v1/health/ready"))
    health = fetcher(urljoin(f"{base_url}/", "v1/health"))
    docs = fetcher(urljoin(f"{base_url}/", "docs"))
    openapi = fetcher(urljoin(f"{base_url}/", "openapi.json"))

    record(
        "liveness",
        live["status"] == 200 and (live["json"] or {}).get("status") == "alive",
        f"HTTP {live['status']}",
    )
    record(
        "readiness",
        ready["status"] == 200 and (ready["json"] or {}).get("status") == "ready",
        f"HTTP {ready['status']}",
    )
    record(
        "release_identity",
        health["status"] == 200 and (health["json"] or {}).get("release") == release_sha,
        f"HTTP {health['status']}",
    )
    headers = health["headers"]
    expected_headers = {
        "cache-control": "no-store",
        "referrer-policy": "no-referrer",
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
    }
    for name, expected in expected_headers.items():
        record(
            f"header_{name}",
            headers.get(name) == expected,
            "present" if name in headers else "missing",
        )
    hsts = headers.get("strict-transport-security", "")
    record("header_hsts", "max-age=" in hsts, "present" if hsts else "missing")
    record("docs_hidden", docs["status"] == 404, f"HTTP {docs['status']}")
    record("openapi_hidden", openapi["status"] == 404, f"HTTP {openapi['status']}")

    return {
        "schema_version": 1,
        "base_url": base_url,
        "release_sha": release_sha,
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the public RecyclerOS production HTTPS surface."
    )
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--release-sha", required=True)
    parser.add_argument("--minimum-certificate-days", type=int, default=14)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = evaluate_endpoint(
        base_url=args.base_url.rstrip("/"),
        release_sha=args.release_sha,
        minimum_certificate_days=args.minimum_certificate_days,
    )
    serialized = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
