from fastapi.testclient import TestClient

from main import app


client = TestClient(app)

TENANT_HEADERS = {
    "X-Organization-ID": "org-rc1",
    "X-Workspace-ID": "workspace-ops",
}


def test_opportunities_reject_missing_tenant_context():
    response = client.get("/v1/opportunities")

    assert response.status_code == 400
    assert "headers are required" in response.json()["detail"]


def test_opportunity_create_accepts_matching_tenant_context():
    response = client.post(
        "/v1/opportunities",
        headers=TENANT_HEADERS,
        json={
            "organization_id": "org-rc1",
            "workspace_id": "workspace-ops",
            "title": "Auction lead",
            "procurement_intent": "partOut",
            "source_type": "manual",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["organization_id"] == "org-rc1"
    assert body["workspace_id"] == "workspace-ops"


def test_opportunity_create_rejects_mismatched_organization():
    response = client.post(
        "/v1/opportunities",
        headers=TENANT_HEADERS,
        json={
            "organization_id": "org-other",
            "workspace_id": "workspace-ops",
            "title": "Bad tenant",
        },
    )

    assert response.status_code == 403
    assert "organization_id" in response.json()["detail"]


def test_vehicle_record_requires_tenant_context():
    response = client.get("/v1/vehicles/VEH-000001")

    assert response.status_code == 400


def test_inventory_create_rejects_mismatched_workspace():
    response = client.post(
        "/v1/inventory",
        headers=TENANT_HEADERS,
        json={
            "organization_id": "org-rc1",
            "workspace_id": "workspace-other",
            "part_name": "ECM / PCM",
        },
    )

    assert response.status_code == 403
    assert "workspace_id" in response.json()["detail"]
