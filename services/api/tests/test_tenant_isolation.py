import pytest
from fastapi.testclient import TestClient

from auth import LocalAuthService, LocalUser, Role, TenantMembership
from main import create_app


PRIMARY_TENANT = {
    "X-Organization-ID": "org-rc1",
    "X-Workspace-ID": "workspace-ops",
}
OTHER_TENANT = {
    "X-Organization-ID": "org-other",
    "X-Workspace-ID": "workspace-other",
}


@pytest.fixture()
def client():
    memberships = (
        TenantMembership(
            organization_id="org-rc1",
            organization_name="RC1 Organization",
            workspace_id="workspace-ops",
            workspace_name="Operations",
            role=Role.OPERATOR,
        ),
        TenantMembership(
            organization_id="org-other",
            organization_name="Other Organization",
            workspace_id="workspace-other",
            workspace_name="Other Workspace",
            role=Role.OPERATOR,
        ),
    )
    user = LocalUser.from_password(
        user_id="user-isolation",
        email="isolation@example.com",
        display_name="Isolation Operator",
        password="isolation-test",
        memberships=memberships,
        password_iterations=1_000,
    )
    auth_service = LocalAuthService([user])
    with TestClient(create_app(auth_service=auth_service)) as test_client:
        yield test_client


@pytest.fixture()
def authorization(client):
    response = client.post(
        "/v1/auth/login",
        json={"email": "isolation@example.com", "password": "isolation-test"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture()
def tenant_headers(authorization):
    return {**authorization, **PRIMARY_TENANT}


@pytest.fixture()
def other_tenant_headers(authorization):
    return {**authorization, **OTHER_TENANT}


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
def test_tenant_scoped_gets_reject_missing_context(client, authorization, path):
    response = client.get(path, headers=authorization)

    assert response.status_code == 400
    assert "headers are required" in response.json()["detail"]


def test_opportunity_create_accepts_matching_tenant_context(client, tenant_headers):
    response = client.post(
        "/v1/opportunities",
        headers=tenant_headers,
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


def test_opportunity_create_rejects_mismatched_organization(client, tenant_headers):
    response = client.post(
        "/v1/opportunities",
        headers=tenant_headers,
        json={
            "organization_id": "org-other",
            "workspace_id": "workspace-ops",
            "title": "Bad tenant",
        },
    )

    assert response.status_code == 403
    assert "organization_id" in response.json()["detail"]


def test_vehicle_record_requires_tenant_context(client, authorization):
    response = client.get("/v1/vehicles/VEH-000001", headers=authorization)

    assert response.status_code == 400


def test_inventory_create_rejects_mismatched_workspace(client, tenant_headers):
    response = client.post(
        "/v1/inventory",
        headers=tenant_headers,
        json={
            "organization_id": "org-rc1",
            "workspace_id": "workspace-other",
            "part_name": "ECM / PCM",
        },
    )

    assert response.status_code == 403
    assert "workspace_id" in response.json()["detail"]


def test_cross_tenant_opportunity_is_not_disclosed(
    client,
    tenant_headers,
    other_tenant_headers,
):
    create_response = client.post(
        "/v1/opportunities",
        headers=tenant_headers,
        json={"title": "Tenant-owned opportunity"},
    )
    opportunity_id = create_response.json()["opportunity_id"]

    get_response = client.get(
        f"/v1/opportunities/{opportunity_id}",
        headers=other_tenant_headers,
    )
    procurement_response = client.get(
        f"/v1/procurement/{opportunity_id}/analysis",
        headers=other_tenant_headers,
    )

    assert get_response.status_code == 404
    assert procurement_response.status_code == 404


def test_cross_tenant_linked_resource_is_rejected(
    client,
    tenant_headers,
    other_tenant_headers,
):
    opportunity = client.post(
        "/v1/opportunities",
        headers=tenant_headers,
        json={"title": "Vehicle source"},
    ).json()
    vehicle = client.post(
        "/v1/vehicles",
        headers=tenant_headers,
        json={"opportunity_id": opportunity["opportunity_id"], "make": "Ford"},
    ).json()

    response = client.post(
        "/v1/pick-list",
        headers=other_tenant_headers,
        json={"vehicle_id": vehicle["vehicle_id"], "yard_name": "Other Yard"},
    )

    assert response.status_code == 404


def test_cross_tenant_vehicle_mileage_update_is_not_disclosed(
    client,
    tenant_headers,
    other_tenant_headers,
):
    opportunity = client.post(
        "/v1/opportunities",
        headers=tenant_headers,
        json={"title": "Mileage source"},
    ).json()
    vehicle = client.post(
        "/v1/vehicles",
        headers=tenant_headers,
        json={"opportunity_id": opportunity["opportunity_id"], "make": "Ford"},
    ).json()

    response = client.patch(
        f"/v1/vehicles/{vehicle['vehicle_code']}/mileage",
        headers=other_tenant_headers,
        json={"mileage": 100000},
    )

    assert response.status_code == 404


def test_cross_tenant_procurement_decision_is_not_disclosed(
    client,
    tenant_headers,
    other_tenant_headers,
):
    opportunity = client.post(
        "/v1/opportunities",
        headers=tenant_headers,
        json={"title": "Decision source"},
    ).json()

    response = client.patch(
        f"/v1/procurement/{opportunity['opportunity_id']}/decision",
        headers=other_tenant_headers,
        json={"intent": "resale"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/v1/vehicles/VEH-UNKNOWN/mileage", {"mileage": 100000}),
        (
            "/v1/procurement/OPP-UNKNOWN/decision",
            {"intent": "personalUse"},
        ),
    ],
)
def test_tenant_scoped_updates_reject_missing_context(
    client,
    authorization,
    path,
    payload,
):
    response = client.patch(path, headers=authorization, json=payload)

    assert response.status_code == 400


def test_cross_tenant_pick_list_update_is_not_disclosed(
    client,
    tenant_headers,
    other_tenant_headers,
):
    opportunity = client.post(
        "/v1/opportunities",
        headers=tenant_headers,
        json={"title": "Availability source"},
    ).json()
    vehicle = client.post(
        "/v1/vehicles",
        headers=tenant_headers,
        json={"opportunity_id": opportunity["opportunity_id"], "make": "Ford"},
    ).json()
    pick_list_item = client.post(
        "/v1/pick-list",
        headers=tenant_headers,
        json={"vehicle_id": vehicle["vehicle_id"], "yard_name": "RC1 Yard"},
    ).json()

    response = client.patch(
        f"/v1/pick-list/{pick_list_item['pick_list_item_id']}/availability",
        headers=other_tenant_headers,
        json={"availability_status": "available"},
    )

    assert response.status_code == 404


def test_pick_list_update_rejects_mismatched_payload_tenant(
    client,
    tenant_headers,
):
    response = client.patch(
        "/v1/pick-list/unknown/availability",
        headers=tenant_headers,
        json={
            "organization_id": "org-other",
            "workspace_id": "workspace-ops",
            "availability_status": "available",
        },
    )

    assert response.status_code == 403
