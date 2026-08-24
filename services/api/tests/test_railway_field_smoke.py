import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "scripts"))

from railway_field_smoke import SmokeFailure, run_field_smoke, validate_inputs  # noqa: E402


class FakeFieldSmokeClient:
    base_url = "https://recycleros-api-pilot.up.railway.app"

    def request(
        self,
        method,
        path,
        expected_status,
        *,
        payload=None,
        query=None,
        token=None,
        tenant=None,
    ):
        if path == "/v1/health/live":
            return {"status": "alive"}
        if path == "/v1/health/ready":
            return {"status": "ready"}
        if path == "/v1/health":
            return {"release": "a" * 40}
        if path == "/v1/auth/login":
            return {
                "access_token": "secret-token-that-must-not-be-reported",
                "identity": {
                    "memberships": [
                        {
                            "organization_id": "org-pilot",
                            "workspace_id": "workspace-pilot",
                            "role": "operator",
                        }
                    ]
                },
            }
        if path == "/v1/auth/me":
            if expected_status == 401:
                return {"detail": "Authentication is required."}
            return {"email": "operator@effortlesssmoke.com"}
        if path == "/v1/opportunities" and expected_status in {400, 403}:
            return {"detail": "rejected"}
        if path == "/v1/opportunities" and method == "POST":
            return {
                "opportunity_id": "opportunity-1",
                "opportunity_code": "OPP-000001",
            }
        if path == "/v1/opportunities":
            return {"items": [{"opportunity_id": "opportunity-1"}]}
        if path == "/v1/vehicles" and method == "POST":
            return {
                "vehicle_id": "vehicle-1",
                "vehicle_code": "VEH-000001",
            }
        if path == "/v1/vehicles/VEH-000001":
            return {"opportunity_id": "opportunity-1"}
        if path == "/v1/procurement/opportunity-1/analysis":
            return {
                "recommended_intent": "partOut",
                "scenarios": [{}, {}, {}],
            }
        if path == "/v1/pick-list" and method == "POST":
            return {"pick_list_item_id": "pick-1"}
        if path == "/v1/pick-list/pick-1/availability":
            return {"availability_status": "available"}
        if path == "/v1/harvest/focus-point/start":
            return {"harvest_session_id": "harvest-1"}
        if path == "/v1/harvest/focus-point/complete":
            return {"timer_status": "stopped"}
        if path == "/v1/inventory" and method == "POST":
            return {
                "inventory_item_id": "inventory-1",
                "inventory_code": "INV-000001",
            }
        if path == "/v1/inventory":
            return {"items": [{"inventory_item_id": "inventory-1"}]}
        if path == "/v1/auth/logout":
            return None
        raise AssertionError(f"Unexpected request: {method} {path} {expected_status}")


def test_field_smoke_covers_complete_path_without_reporting_credentials():
    report = run_field_smoke(
        FakeFieldSmokeClient(),
        email="operator@effortlesssmoke.com",
        password="secret-password-that-must-not-be-reported",
        expected_release_sha="a" * 40,
        run_id="20260824120000-12345678",
        executed_at="2026-08-24T12:00:00+00:00",
    )

    assert report["passed"] is True
    assert report["records"] == {
        "opportunity_code": "OPP-000001",
        "vehicle_code": "VEH-000001",
        "inventory_code": "INV-000001",
    }
    names = {check["name"] for check in report["checks"]}
    assert {
        "login",
        "organization_workspace_selection",
        "mission_control_data",
        "opportunity_discovery",
        "vehicle_record",
        "procurement",
        "pick_list",
        "focus_point",
        "inventory_intake",
        "logout",
        "revoked_session_rejected",
    } <= names
    serialized = json.dumps(report)
    assert "secret-password" not in serialized
    assert "secret-token" not in serialized


def test_field_smoke_requires_exact_https_origin_and_release_sha():
    with pytest.raises(SmokeFailure, match="exact HTTPS origin"):
        validate_inputs("http://example.com", "a" * 40)
    with pytest.raises(SmokeFailure, match="complete Git SHA"):
        validate_inputs("https://example.com", "short")
