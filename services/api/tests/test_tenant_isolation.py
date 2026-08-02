import pytest
from fastapi.testclient import TestClient

from main import create_app


TENANT_HEADERS = {
    "X-Organization-ID": "org-rc1",
    "X-Workspace-ID": "workspace-ops",
}
OTHER_TENANT_HEADERS = {
    "X-Organization-ID": "org-other",
    "X-Workspace-ID": "workspace-other",
}


@pytest.fixture()
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.mark.parametrize(
    "path",
    [
        "/v1/opportunities",
        "/v1/vehicles/VEH-UNKNOWN",
        "/v1/procurement/OPP-UNKNOWN/analysis",
        "/v1/pick-list",
        "/v1/inventory",
    ],
)
def test_tenant_scoped_gets_reject_missing_context(client, path):
    response = client.get(path)

    assert response.status_code == 400
    assert "headers are required" in response.json()["detail"]


def test_opportunities_reject_missing_tenant_context():
    response = TestClient(create_app()).get("/v1/opportunities")

    assert response.status_code == 400
    assert "headers are required" in response.json()["detail"]


def test_opportunity_create_accepts_matching_tenant_context(client):
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

    assert response.status_code == 201
    body = response.json()
    assert body["organization_id"] == "org-rc1"
    assert body["workspace_id"] == "workspace-ops"


def test_opportunity_create_rejects_mismatched_organization(client):
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


def test_vehicle_record_requires_tenant_context(client):
    response = client.get("/v1/vehicles/VEH-000001")

    assert response.status_code == 400


def test_inventory_create_rejects_mismatched_workspace(client):
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


def test_cross_tenant_opportunity_is_not_disclosed(client):
    create_response = client.post(
        "/v1/opportunities",
        headers=TENANT_HEADERS,
        json={"title": "Tenant-owned opportunity"},
    )
    opportunity_id = create_response.json()["opportunity_id"]

    get_response = client.get(
        f"/v1/opportunities/{opportunity_id}", headers=OTHER_TENANT_HEADERS
    )
    procurement_response = client.get(
        f"/v1/procurement/{opportunity_id}/analysis",
        headers=OTHER_TENANT_HEADERS,
    )

    assert get_response.status_code == 404
    assert procurement_response.status_code == 404


def test_cross_tenant_linked_resource_is_rejected(client):
    opportunity = client.post(
        "/v1/opportunities",
        headers=TENANT_HEADERS,
        json={"title": "Vehicle source"},
    ).json()
    vehicle = client.post(
        "/v1/vehicles",
        headers=TENANT_HEADERS,
        json={"opportunity_id": opportunity["opportunity_id"], "make": "Ford"},
    ).json()

    response = client.post(
        "/v1/pick-list",
        headers=OTHER_TENANT_HEADERS,
        json={"vehicle_id": vehicle["vehicle_id"], "yard_name": "Other Yard"},
    )

    assert response.status_code == 404
