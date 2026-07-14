from fastapi.testclient import TestClient

from main import create_app


TENANT_HEADERS = {
    "X-Organization-ID": "org-rc1",
    "X-Workspace-ID": "workspace-ops",
}


def test_rc1_backend_workflow():
    with TestClient(create_app()) as client:
        health = client.get("/v1/health")
        assert health.status_code == 200
        assert health.json()["storage"] == "memory"

        opportunity_response = client.post(
            "/v1/opportunities",
            headers=TENANT_HEADERS,
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
            "/v1/opportunities", headers=TENANT_HEADERS
        ).json()
        assert [item["opportunity_id"] for item in opportunity_list["items"]] == [
            opportunity["opportunity_id"]
        ]

        vehicle_response = client.post(
            "/v1/vehicles",
            headers=TENANT_HEADERS,
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
            f"/v1/vehicles/{vehicle['vehicle_code']}", headers=TENANT_HEADERS
        ).json()
        assert vehicle_record["opportunity_id"] == opportunity["opportunity_id"]

        procurement_response = client.get(
            f"/v1/procurement/{opportunity['opportunity_id']}/analysis",
            headers=TENANT_HEADERS,
        )
        assert procurement_response.status_code == 200
        procurement = procurement_response.json()
        assert procurement["recommended_intent"] == "partOut"
        assert len(procurement["scenarios"]) == 3

        pick_list_response = client.post(
            "/v1/pick-list",
            headers=TENANT_HEADERS,
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
            headers=TENANT_HEADERS,
            json={"availability_status": "available"},
        )
        assert availability_response.status_code == 200
        assert availability_response.json()["availability_status"] == "available"

        pick_list = client.get("/v1/pick-list", headers=TENANT_HEADERS).json()
        assert pick_list["items"][0]["vehicle_id"] == vehicle["vehicle_id"]
        assert pick_list["items"][0]["availability_status"] == "available"

        session_response = client.post(
            "/v1/harvest/focus-point/start",
            headers=TENANT_HEADERS,
            params={"vehicle_id": vehicle["vehicle_id"]},
        )
        assert session_response.status_code == 201
        session = session_response.json()
        assert session["timer_status"] == "active"

        complete_response = client.post(
            "/v1/harvest/focus-point/complete",
            headers=TENANT_HEADERS,
            params={"harvest_session_id": session["harvest_session_id"]},
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["timer_status"] == "stopped"

        inventory_response = client.post(
            "/v1/inventory",
            headers=TENANT_HEADERS,
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

        inventory_list = client.get("/v1/inventory", headers=TENANT_HEADERS).json()
        assert [item["inventory_item_id"] for item in inventory_list["items"]] == [
            inventory_item["inventory_item_id"]
        ]
        assert inventory_item["organization_id"] == TENANT_HEADERS["X-Organization-ID"]
        assert inventory_item["workspace_id"] == TENANT_HEADERS["X-Workspace-ID"]
