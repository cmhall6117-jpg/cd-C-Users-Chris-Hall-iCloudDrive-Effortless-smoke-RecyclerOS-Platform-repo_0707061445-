import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen
from uuid import uuid4


class SmokeFailure(RuntimeError):
    pass


class FieldSmokeClient:
    def __init__(self, base_url: str, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        expected_status: int,
        *,
        payload: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
        token: str | None = None,
        tenant: dict[str, str] | None = None,
    ) -> dict[str, Any] | None:
        url = urljoin(f"{self.base_url}/", path.lstrip("/"))
        if query:
            url = f"{url}?{urlencode(query)}"
        headers = {"Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if tenant:
            headers["X-Organization-ID"] = tenant["organization_id"]
            headers["X-Workspace-ID"] = tenant["workspace_id"]
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                status = response.status
                response_body = response.read()
        except HTTPError as exc:
            status = exc.code
            response_body = exc.read()
        except (URLError, TimeoutError) as exc:
            raise SmokeFailure(f"{method} {path} could not reach the pilot API.") from exc

        if status != expected_status:
            raise SmokeFailure(
                f"{method} {path} returned HTTP {status}; expected {expected_status}."
            )
        if not response_body:
            return None
        try:
            return json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SmokeFailure(f"{method} {path} returned invalid JSON.") from exc


def validate_inputs(base_url: str, expected_release_sha: str) -> None:
    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        raise SmokeFailure("Pilot API URL must be an exact HTTPS origin.")
    if not re.fullmatch(r"[0-9a-f]{40}", expected_release_sha):
        raise SmokeFailure("Expected release SHA must be a complete Git SHA.")


def run_field_smoke(
    client: FieldSmokeClient,
    *,
    email: str,
    password: str,
    expected_release_sha: str,
    run_id: str,
    executed_at: str,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []

    def record(name: str, detail: str) -> None:
        checks.append({"name": name, "status": "passed", "detail": detail})

    live = client.request("GET", "/v1/health/live", 200)
    if not live or live.get("status") != "alive":
        raise SmokeFailure("Liveness response did not report alive.")
    record("liveness", "HTTP 200")

    ready = client.request("GET", "/v1/health/ready", 200)
    if not ready or ready.get("status") != "ready":
        raise SmokeFailure("Readiness response did not report ready.")
    record("readiness", "HTTP 200")

    health = client.request("GET", "/v1/health", 200)
    if not health or health.get("release") != expected_release_sha:
        raise SmokeFailure("Live release identity does not match the approved SHA.")
    record("release_identity", expected_release_sha)

    login = client.request(
        "POST",
        "/v1/auth/login",
        200,
        payload={"email": email, "password": password},
    )
    if not login or not login.get("access_token"):
        raise SmokeFailure("Login did not return an access token.")
    token = login["access_token"]
    memberships = login.get("identity", {}).get("memberships", [])
    if len(memberships) != 1:
        raise SmokeFailure("The one-person pilot requires exactly one membership.")
    membership = memberships[0]
    tenant = {
        "organization_id": membership["organization_id"],
        "workspace_id": membership["workspace_id"],
    }
    record("login", "HTTP 200")
    record("organization_workspace_selection", membership["role"])

    identity = client.request("GET", "/v1/auth/me", 200, token=token)
    if not identity or identity.get("email") != email:
        raise SmokeFailure("Authenticated identity does not match the field tester.")
    record("authenticated_identity", "HTTP 200")

    client.request("GET", "/v1/opportunities", 400, token=token)
    record("missing_tenant_rejected", "HTTP 400")
    client.request(
        "GET",
        "/v1/opportunities",
        403,
        token=token,
        tenant={
            "organization_id": tenant["organization_id"],
            "workspace_id": "workspace-field-smoke-mismatch",
        },
    )
    record("mismatched_tenant_rejected", "HTTP 403")

    client.request("GET", "/v1/opportunities", 200, token=token, tenant=tenant)
    record("mission_control_data", "HTTP 200")

    numeric_id = "".join(character for character in run_id if character.isdigit())[-10:]
    vin = f"1RCYS26{numeric_id.zfill(10)}"
    opportunity = client.request(
        "POST",
        "/v1/opportunities",
        201,
        token=token,
        tenant=tenant,
        payload={
            "title": f"Railway one-person field smoke {run_id}",
            "source_type": "manual",
            "procurement_intent": "partOut",
            "vin": vin,
            "year": 2019,
            "make": "Ford",
            "model": "F-150",
            "estimated_max_bid": 3200,
            "estimated_net_profit": 1800,
            "confidence_score": 85,
        },
    )
    if not opportunity:
        raise SmokeFailure("Opportunity creation returned no record.")
    record("opportunity_discovery", opportunity["opportunity_code"])

    opportunities = client.request(
        "GET", "/v1/opportunities", 200, token=token, tenant=tenant
    )
    if opportunity["opportunity_id"] not in {
        item["opportunity_id"] for item in (opportunities or {}).get("items", [])
    }:
        raise SmokeFailure("Created opportunity was not visible in its tenant.")
    record("opportunity_list", "created record visible")

    vehicle = client.request(
        "POST",
        "/v1/vehicles",
        201,
        token=token,
        tenant=tenant,
        payload={
            "opportunity_id": opportunity["opportunity_id"],
            "vin": vin,
            "year": 2019,
            "make": "Ford",
            "model": "F-150",
            "mileage": 126000,
        },
    )
    if not vehicle:
        raise SmokeFailure("Vehicle creation returned no record.")
    vehicle_record = client.request(
        "GET",
        f"/v1/vehicles/{vehicle['vehicle_code']}",
        200,
        token=token,
        tenant=tenant,
    )
    if not vehicle_record or vehicle_record.get("opportunity_id") != opportunity[
        "opportunity_id"
    ]:
        raise SmokeFailure("Vehicle record did not preserve the opportunity link.")
    record("vehicle_record", vehicle["vehicle_code"])

    procurement = client.request(
        "GET",
        f"/v1/procurement/{opportunity['opportunity_id']}/analysis",
        200,
        token=token,
        tenant=tenant,
    )
    if (
        not procurement
        or procurement.get("recommended_intent") != "partOut"
        or len(procurement.get("scenarios", [])) != 3
    ):
        raise SmokeFailure("Procurement analysis did not return the RC1 scenarios.")
    record("procurement", "3 scenarios; partOut recommended")

    pick_item = client.request(
        "POST",
        "/v1/pick-list",
        201,
        token=token,
        tenant=tenant,
        payload={
            "vehicle_id": vehicle["vehicle_id"],
            "yard_name": "Effortless Smoke Pilot Yard",
            "yard_row": "FIELD-01",
        },
    )
    if not pick_item:
        raise SmokeFailure("Pick-list creation returned no record.")
    available_pick = client.request(
        "PATCH",
        f"/v1/pick-list/{pick_item['pick_list_item_id']}/availability",
        200,
        token=token,
        tenant=tenant,
        payload={"availability_status": "available"},
    )
    if not available_pick or available_pick.get("availability_status") != "available":
        raise SmokeFailure("Pick-list availability did not become available.")
    record("pick_list", "available")

    harvest = client.request(
        "POST",
        "/v1/harvest/focus-point/start",
        201,
        token=token,
        tenant=tenant,
        query={"vehicle_id": vehicle["vehicle_id"]},
    )
    if not harvest:
        raise SmokeFailure("Focus Point start returned no session.")
    completed_harvest = client.request(
        "POST",
        "/v1/harvest/focus-point/complete",
        200,
        token=token,
        tenant=tenant,
        query={"harvest_session_id": harvest["harvest_session_id"]},
    )
    if not completed_harvest or completed_harvest.get("timer_status") != "stopped":
        raise SmokeFailure("Focus Point session did not stop.")
    record("focus_point", "completed")

    inventory = client.request(
        "POST",
        "/v1/inventory",
        201,
        token=token,
        tenant=tenant,
        payload={
            "part_name": f"Field Smoke ECM {run_id}",
            "source_vehicle_id": vehicle["vehicle_id"],
            "harvest_session_id": harvest["harvest_session_id"],
            "storage_location_id": "FIELD-01-A12",
            "condition": "usedUntested",
            "status": "available",
            "quantity": 1,
            "estimated_value": 225,
        },
    )
    if not inventory:
        raise SmokeFailure("Inventory intake returned no record.")
    inventory_items = client.request(
        "GET", "/v1/inventory", 200, token=token, tenant=tenant
    )
    if inventory["inventory_item_id"] not in {
        item["inventory_item_id"]
        for item in (inventory_items or {}).get("items", [])
    }:
        raise SmokeFailure("Inventory item was not visible in its tenant.")
    record("inventory_intake", inventory["inventory_code"])

    client.request("POST", "/v1/auth/logout", 204, token=token)
    record("logout", "HTTP 204")
    client.request("GET", "/v1/auth/me", 401, token=token)
    record("revoked_session_rejected", "HTTP 401")

    return {
        "schema_version": 1,
        "run_id": run_id,
        "executed_at": executed_at,
        "base_url": client.base_url,
        "release_sha": expected_release_sha,
        "tester": email,
        "scope": "one_person_synthetic_field_smoke",
        "passed": True,
        "tenant": {
            "organization_id": tenant["organization_id"],
            "workspace_id": tenant["workspace_id"],
            "role": membership["role"],
        },
        "records": {
            "opportunity_code": opportunity["opportunity_code"],
            "vehicle_code": vehicle["vehicle_code"],
            "inventory_code": inventory["inventory_code"],
        },
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the sanitized RecyclerOS one-person Railway field smoke."
    )
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--release-sha", required=True)
    parser.add_argument("--email", default="operator@effortlesssmoke.com")
    parser.add_argument(
        "--password-env", default="RECYCLEROS_LOCAL_OPERATOR_PASSWORD"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    validate_inputs(base_url, args.release_sha)
    password = os.getenv(args.password_env)
    if not password:
        raise SmokeFailure(
            f"Required operator password environment variable {args.password_env} is missing."
        )
    executed_at = datetime.now(timezone.utc).isoformat()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + uuid4().hex[:8]
    report = run_field_smoke(
        FieldSmokeClient(base_url),
        email=args.email,
        password=password,
        expected_release_sha=args.release_sha,
        run_id=run_id,
        executed_at=executed_at,
    )
    serialized = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
