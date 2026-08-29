from fastapi.testclient import TestClient

from auth import LocalAuthService, LocalUser, Role, TenantMembership
from main import create_app


TENANT_HEADERS = {
    "X-Organization-ID": "org-local",
    "X-Workspace-ID": "workspace-local",
}


def test_rc1_backend_workflow():
    membership = TenantMembership(
        organization_id="org-local",
        organization_name="Effortless Smoke, LLC",
        workspace_id="workspace-local",
        workspace_name="RecyclerOS Operations",
        role=Role.OPERATOR,
    )
    user = LocalUser.from_password(
        user_id="user-workflow",
        email="operator@effortlesssmoke.com",
        display_name="Workflow Operator",
        password="local-rc1",
        memberships=(membership,),
        password_iterations=1_000,
    )
    auth_service = LocalAuthService([user])
    with TestClient(create_app(auth_service=auth_service)) as client:
        health = client.get("/v1/health")
        assert health.status_code == 200
        assert health.json()["storage"] == "memory"

        login = client.post(
            "/v1/auth/login",
            json={
                "email": "operator@effortlesssmoke.com",
                "password": "local-rc1",
            },
        )
        assert login.status_code == 200
        headers = {
            **TENANT_HEADERS,
            "Authorization": f"Bearer {login.json()['access_token']}",
        }

        opportunity_response = client.post(
            "/v1/opportunities",
            headers=headers,
            json={
                "title": "2019 Ford F-150 auction lead",
                "procurement_intent": "partOut",
                "vin": "1FTFW1E50KFA00001",
                "year": 2019,
                "make": "Ford",
                "model": "F-150",
            },
        )
        assert opportunity_response.status_code == 201
        opportunity = opportunity_response.json()

        opportunity_list = client.get(
            "/v1/opportunities", headers=headers
        ).json()
        assert [item["opportunity_id"] for item in opportunity_list["items"]] == [
            opportunity["opportunity_id"]
        ]

        vehicle_response = client.post(
            "/v1/vehicles",
            headers=headers,
            json={
                "opportunity_id": opportunity["opportunity_id"],
                "vin": "1FTFW1E50KFA00001",
                "year": 2019,
                "make": "Ford",
                "model": "F-150",
                "mileage": 126000,
            },
        )
        assert vehicle_response.status_code == 201
        vehicle = vehicle_response.json()

        vehicle_record = client.get(
            f"/v1/vehicles/{vehicle['vehicle_code']}", headers=headers
        ).json()
        assert vehicle_record["opportunity_id"] == opportunity["opportunity_id"]

        mileage_response = client.patch(
            f"/v1/vehicles/{vehicle['vehicle_code']}/mileage",
            headers=headers,
            json={"mileage": 141500},
        )
        assert mileage_response.status_code == 200
        assert mileage_response.json()["mileage"] == 141500

        procurement_response = client.get(
            f"/v1/procurement/{opportunity['opportunity_id']}/analysis",
            headers=headers,
        )
        assert procurement_response.status_code == 200
        procurement = procurement_response.json()
        assert procurement["recommended_intent"] == "partOut"
        assert len(procurement["scenarios"]) == 3

        resale_decision_response = client.patch(
            f"/v1/procurement/{opportunity['opportunity_id']}/decision",
            headers=headers,
            json={"intent": "resale"},
        )
        assert resale_decision_response.status_code == 200
        assert resale_decision_response.json()["procurement_intent"] == "resale"

        personal_decision_response = client.patch(
            f"/v1/procurement/{opportunity['opportunity_id']}/decision",
            headers=headers,
            json={"intent": "personalUse"},
        )
        assert personal_decision_response.status_code == 200
        assert personal_decision_response.json()["procurement_intent"] == "personalUse"

        part_out_decision_response = client.patch(
            f"/v1/procurement/{opportunity['opportunity_id']}/decision",
            headers=headers,
            json={"intent": "partOut"},
        )
        assert part_out_decision_response.status_code == 200
        assert part_out_decision_response.json()["procurement_intent"] == "partOut"

        pick_list_response = client.post(
            "/v1/pick-list",
            headers=headers,
            json={
                "vehicle_id": vehicle["vehicle_id"],
                "yard_name": "Effortless Smoke Yard",
                "yard_row": "A-12",
            },
        )
        assert pick_list_response.status_code == 201
        pick_list_item = pick_list_response.json()

        availability_response = client.patch(
            f"/v1/pick-list/{pick_list_item['pick_list_item_id']}/availability",
            headers=headers,
            json={"availability_status": "available"},
        )
        assert availability_response.status_code == 200
        assert availability_response.json()["availability_status"] == "available"

        pick_list = client.get("/v1/pick-list", headers=headers).json()
        assert pick_list["items"][0]["vehicle_id"] == vehicle["vehicle_id"]
        assert pick_list["items"][0]["availability_status"] == "available"

        session_response = client.post(
            "/v1/harvest/focus-point/start",
            headers=headers,
            params={"vehicle_id": vehicle["vehicle_id"]},
        )
        assert session_response.status_code == 201
        session = session_response.json()
        assert session["timer_status"] == "active"

        complete_response = client.post(
            "/v1/harvest/focus-point/complete",
            headers=headers,
            params={"harvest_session_id": session["harvest_session_id"]},
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["timer_status"] == "stopped"

        inventory_response = client.post(
            "/v1/inventory",
            headers=headers,
            json={
                "part_name": "ECM / PCM",
                "source_vehicle_id": vehicle["vehicle_id"],
                "harvest_session_id": session["harvest_session_id"],
                "quantity": 1,
                "estimated_value": 225.00,
            },
        )
        assert inventory_response.status_code == 201
        inventory_item = inventory_response.json()

        inventory_list = client.get("/v1/inventory", headers=headers).json()
        assert [item["inventory_item_id"] for item in inventory_list["items"]] == [
            inventory_item["inventory_item_id"]
        ]
        assert inventory_item["organization_id"] == TENANT_HEADERS["X-Organization-ID"]
        assert inventory_item["workspace_id"] == TENANT_HEADERS["X-Workspace-ID"]
