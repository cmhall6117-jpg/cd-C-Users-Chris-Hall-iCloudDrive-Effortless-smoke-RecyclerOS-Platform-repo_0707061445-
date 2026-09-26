import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth import LocalAuthService, LocalUser, Role, TenantMembership
from main import create_app
from postgres_store import PostgresStore
from store import InMemoryStore


@pytest.fixture(params=["memory", "postgres"])
def inventory_api(request):
    database_url = os.getenv("DATABASE_URL")
    if request.param == "postgres" and not database_url:
        pytest.skip("DATABASE_URL is required for PostgreSQL provenance evidence")

    suffix = uuid4().hex
    memberships = tuple(
        TenantMembership(
            organization_id=f"org-provenance-{label}-{suffix}",
            organization_name=f"Provenance {label}",
            workspace_id=f"workspace-provenance-{label}-{suffix}",
            workspace_name=f"Provenance {label}",
            role=Role.OPERATOR,
        )
        for label in ("primary", "other")
    )
    store = (
        PostgresStore(database_url)
        if request.param == "postgres"
        else InMemoryStore()
    )
    if request.param == "postgres":
        with store._connect() as conn, conn.cursor() as cursor:
            for membership in memberships:
                cursor.execute(
                    "INSERT INTO organizations (id, name) VALUES (%s, %s)",
                    (membership.organization_id, membership.organization_name),
                )
                cursor.execute(
                    "INSERT INTO workspaces (id, organization_id, name) "
                    "VALUES (%s, %s, %s)",
                    (
                        membership.workspace_id,
                        membership.organization_id,
                        membership.workspace_name,
                    ),
                )

    user = LocalUser.from_password(
        user_id=f"user-provenance-{suffix}",
        email="provenance@example.com",
        display_name="Provenance Operator",
        password="provenance-test-password",
        memberships=memberships,
        password_iterations=1_000,
    )
    try:
        with TestClient(
            create_app(store=store, auth_service=LocalAuthService([user]))
        ) as client:
            login = client.post(
                "/v1/auth/login",
                json={"email": user.email, "password": "provenance-test-password"},
            )
            assert login.status_code == 200
            headers = [
                {
                    "Authorization": f"Bearer {login.json()['access_token']}",
                    "X-Organization-ID": membership.organization_id,
                    "X-Workspace-ID": membership.workspace_id,
                }
                for membership in memberships
            ]
            yield client, headers[0], headers[1], store
    finally:
        if request.param == "postgres":
            # Delete only this test's rows; do not reset shared runtime/auth data.
            with store._connect() as conn, conn.cursor() as cursor:
                for membership in memberships:
                    tenant = (membership.organization_id,)
                    for table in (
                        "inventory_items",
                        "harvest_sessions",
                        "vehicle_timeline",
                        "vehicles",
                        "storage_locations",
                        "workspaces",
                    ):
                        cursor.execute(
                            f"DELETE FROM {table} WHERE organization_id = %s",
                            tenant,
                        )
                    cursor.execute("DELETE FROM organizations WHERE id = %s", tenant)


def _create_vehicle(client, headers):
    response = client.post("/v1/vehicles", headers=headers, json={"make": "Test"})
    assert response.status_code == 201
    return response.json()["vehicle_id"]


def _start_session(client, headers, vehicle_id):
    response = client.post(
        "/v1/harvest/focus-point/start",
        headers=headers,
        params={"vehicle_id": vehicle_id},
    )
    assert response.status_code == 201
    return response.json()["harvest_session_id"]


def _inventory(client, headers):
    response = client.get("/v1/inventory", headers=headers)
    assert response.status_code == 200
    return response.json()["items"]


def _storage_locations(store, headers):
    if store.storage_name != "postgres":
        # The memory store has no separate storage-location collection.
        return None
    with store._connect() as conn, conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, location_code, name FROM storage_locations "
            "WHERE organization_id = %s AND workspace_id = %s ORDER BY id",
            (headers["X-Organization-ID"], headers["X-Workspace-ID"]),
        )
        return cursor.fetchall()


def test_inventory_rejects_mismatched_vehicle_and_session_without_side_effects(
    inventory_api,
):
    client, headers, _, store = inventory_api
    vehicle_a = _create_vehicle(client, headers)
    vehicle_b = _create_vehicle(client, headers)
    session_b = _start_session(client, headers, vehicle_b)
    existing = client.post(
        "/v1/inventory",
        headers=headers,
        json={
            "part_name": "Existing part",
            "storage_location_id": f"existing-{uuid4().hex}",
        },
    )
    assert existing.status_code == 201
    inventory_before = _inventory(client, headers)
    locations_before = _storage_locations(store, headers)

    response = client.post(
        "/v1/inventory",
        headers=headers,
        json={
            "part_name": "Mismatched part",
            "source_vehicle_id": vehicle_a,
            "harvest_session_id": session_b,
            "storage_location_id": f"must-not-create-{uuid4().hex}",
        },
    )

    assert response.status_code == 404
    assert _inventory(client, headers) == inventory_before
    assert _storage_locations(store, headers) == locations_before


@pytest.mark.parametrize(
    "links", ["matching", "matching_completed", "vehicle_only", "session_only", "neither"]
)
def test_inventory_accepts_matching_and_optional_provenance(inventory_api, links):
    client, headers, _, _ = inventory_api
    vehicle_id = _create_vehicle(client, headers)
    session_id = _start_session(client, headers, vehicle_id)
    if links == "matching_completed":
        complete = client.post(
            "/v1/harvest/focus-point/complete",
            headers=headers,
            params={"harvest_session_id": session_id},
        )
        assert complete.status_code == 200
    payload = {"part_name": "Valid provenance part"}
    if links in {"matching", "matching_completed", "vehicle_only"}:
        payload["source_vehicle_id"] = vehicle_id
    if links in {"matching", "matching_completed", "session_only"}:
        payload["harvest_session_id"] = session_id

    response = client.post("/v1/inventory", headers=headers, json=payload)

    assert response.status_code == 201
    item = response.json()
    assert item["source_vehicle_id"] == payload.get("source_vehicle_id")
    assert item["harvest_session_id"] == payload.get("harvest_session_id")
    assert (
        _inventory(client, headers)[0]["inventory_item_id"]
        == item["inventory_item_id"]
    )


@pytest.mark.parametrize("foreign_reference", ["vehicle", "session"])
def test_inventory_rejects_cross_tenant_provenance(inventory_api, foreign_reference):
    client, headers, other_headers, store = inventory_api
    own_vehicle = _create_vehicle(client, headers)
    foreign_vehicle = _create_vehicle(client, other_headers)
    own_session = _start_session(client, headers, own_vehicle)
    foreign_session = _start_session(client, other_headers, foreign_vehicle)
    inventory_before = _inventory(client, headers)
    locations_before = _storage_locations(store, headers)

    response = client.post(
        "/v1/inventory",
        headers=headers,
        json={
            "part_name": "Foreign reference part",
            "source_vehicle_id": (
                foreign_vehicle if foreign_reference == "vehicle" else own_vehicle
            ),
            "harvest_session_id": (
                foreign_session if foreign_reference == "session" else own_session
            ),
            "storage_location_id": f"must-not-create-{uuid4().hex}",
        },
    )

    assert response.status_code == 404
    assert _inventory(client, headers) == inventory_before
    assert _storage_locations(store, headers) == locations_before
