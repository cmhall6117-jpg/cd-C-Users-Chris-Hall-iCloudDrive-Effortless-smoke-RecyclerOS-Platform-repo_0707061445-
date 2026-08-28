import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from main import create_app
from postgres_auth import PostgresAuthService
from postgres_store import PostgresStore


DATABASE_URL = os.getenv("DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL is required for PostgreSQL runtime evidence",
)

TENANT_HEADERS = {
    "X-Organization-ID": "org-local",
    "X-Workspace-ID": "workspace-local",
}
OPERATOR_EMAIL = "operator@effortlesssmoke.com"
OPERATOR_PASSWORD = "postgres-runtime-password"


def _reset_auth_state() -> None:
    import psycopg

    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            TRUNCATE TABLE
                auth_audit_events,
                auth_login_attempts,
                auth_sessions,
                auth_tenant_memberships,
                auth_password_credentials,
                auth_users
            CASCADE
            """
        )


def _runtime_auth(*, max_failures: int = 5) -> PostgresAuthService:
    return PostgresAuthService(DATABASE_URL, max_failures=max_failures)


def test_postgres_workflow_auth_persist_and_revoke_across_restart():
    import psycopg

    _reset_auth_state()
    first_auth = _runtime_auth(max_failures=2)
    first_auth.bootstrap_local_operator(OPERATOR_PASSWORD)
    unique_suffix = uuid4().hex[:12]

    with TestClient(
        create_app(store=PostgresStore(DATABASE_URL), auth_service=first_auth)
    ) as first_client:
        health = first_client.get("/v1/health")
        assert health.status_code == 200
        assert health.json()["storage"] == "postgres"
        assert health.json()["auth_storage"] == "postgres"
        readiness = first_client.get("/v1/health/ready")
        assert readiness.status_code == 200
        assert readiness.json()["status"] == "ready"

        login = first_client.post(
            "/v1/auth/login",
            json={"email": OPERATOR_EMAIL, "password": OPERATOR_PASSWORD},
        )
        assert login.status_code == 200
        access_token = login.json()["access_token"]
        headers = {
            **TENANT_HEADERS,
            "Authorization": f"Bearer {access_token}",
        }

        opportunity_response = first_client.post(
            "/v1/opportunities",
            headers=headers,
            json={
                "title": f"Durable RC1 lead {unique_suffix}",
                "procurement_intent": "partOut",
                "vin": f"RC1{unique_suffix}".upper(),
                "year": 2019,
                "make": "Ford",
                "model": "F-150",
            },
        )
        assert opportunity_response.status_code == 201
        opportunity = opportunity_response.json()

        vehicle_response = first_client.post(
            "/v1/vehicles",
            headers=headers,
            json={
                "opportunity_id": opportunity["opportunity_id"],
                "vin": f"RC1{unique_suffix}".upper(),
                "year": 2019,
                "make": "Ford",
                "model": "F-150",
                "mileage": 126000,
            },
        )
        assert vehicle_response.status_code == 201
        vehicle = vehicle_response.json()

        mileage_response = first_client.patch(
            f"/v1/vehicles/{vehicle['vehicle_code']}/mileage",
            headers=headers,
            json={"mileage": 141500},
        )
        assert mileage_response.status_code == 200
        assert mileage_response.json()["mileage"] == 141500

        procurement = first_client.get(
            f"/v1/procurement/{opportunity['opportunity_id']}/analysis",
            headers=headers,
        )
        assert procurement.status_code == 200
        assert len(procurement.json()["scenarios"]) == 3

        decision_response = first_client.patch(
            f"/v1/procurement/{opportunity['opportunity_id']}/decision",
            headers=headers,
            json={"intent": "partOut"},
        )
        assert decision_response.status_code == 200
        assert decision_response.json()["procurement_intent"] == "partOut"

        pick_list_response = first_client.post(
            "/v1/pick-list",
            headers=headers,
            json={
                "vehicle_id": vehicle["vehicle_id"],
                "yard_name": "Effortless Smoke Yard",
                "yard_row": "A-12",
            },
        )
        assert pick_list_response.status_code == 201

        session_response = first_client.post(
            "/v1/harvest/focus-point/start",
            headers=headers,
            params={"vehicle_id": vehicle["vehicle_id"]},
        )
        assert session_response.status_code == 201
        session = session_response.json()

        complete_response = first_client.post(
            "/v1/harvest/focus-point/complete",
            headers=headers,
            params={"harvest_session_id": session["harvest_session_id"]},
        )
        assert complete_response.status_code == 200

        inventory_response = first_client.post(
            "/v1/inventory",
            headers=headers,
            json={
                "part_name": f"ECM {unique_suffix}",
                "source_vehicle_id": vehicle["vehicle_id"],
                "harvest_session_id": session["harvest_session_id"],
                "quantity": 1,
                "estimated_value": 225.00,
            },
        )
        assert inventory_response.status_code == 201
        inventory = inventory_response.json()

    restarted_auth = _runtime_auth(max_failures=2)
    with TestClient(
        create_app(
            store=PostgresStore(DATABASE_URL),
            auth_service=restarted_auth,
        )
    ) as restarted_client:
        restarted_headers = {
            **TENANT_HEADERS,
            "Authorization": f"Bearer {access_token}",
        }
        me = restarted_client.get("/v1/auth/me", headers=restarted_headers)
        opportunities = restarted_client.get(
            "/v1/opportunities", headers=restarted_headers
        )
        inventory_items = restarted_client.get(
            "/v1/inventory", headers=restarted_headers
        )

        assert me.status_code == 200
        assert opportunity["opportunity_id"] in {
            item["opportunity_id"] for item in opportunities.json()["items"]
        }
        assert inventory["inventory_item_id"] in {
            item["inventory_item_id"] for item in inventory_items.json()["items"]
        }
        assert restarted_client.post(
            "/v1/auth/logout", headers=restarted_headers
        ).status_code == 204

    with TestClient(
        create_app(
            store=PostgresStore(DATABASE_URL),
            auth_service=_runtime_auth(max_failures=2),
        )
    ) as third_client:
        revoked = third_client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert revoked.status_code == 401

        for _ in range(2):
            failed = third_client.post(
                "/v1/auth/login",
                json={"email": OPERATOR_EMAIL, "password": "wrong-password"},
            )
            assert failed.status_code == 401
        blocked = third_client.post(
            "/v1/auth/login",
            json={"email": OPERATOR_EMAIL, "password": OPERATOR_PASSWORD},
        )
        assert blocked.status_code == 401

    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT event_type
            FROM auth_audit_events
            WHERE email = %s
            """,
            (OPERATOR_EMAIL,),
        )
        events = {row[0] for row in cursor.fetchall()}
        cursor.execute(
            """
            SELECT failure_count, blocked_until
            FROM auth_login_attempts
            WHERE email = %s
            """,
            (OPERATOR_EMAIL,),
        )
        attempts = cursor.fetchone()

    assert {"login_succeeded", "logout", "login_failed", "login_blocked"} <= events
    assert attempts[0] == 2
    assert attempts[1] is not None


def test_production_owner_bootstrap_is_audited_and_one_time():
    import psycopg

    _reset_auth_state()
    auth_service = _runtime_auth()
    owner_email = "production-owner@example.com"
    owner_password = "production-owner-password"

    user_id = auth_service.bootstrap_production_owner(
        email=owner_email,
        display_name="Production Owner",
        password=owner_password,
        organization_id="org-production",
        organization_name="Effortless Smoke Production",
        workspace_id="workspace-production",
        workspace_name="RecyclerOS Production",
    )

    session = auth_service.authenticate(owner_email, owner_password)
    assert session is not None
    assert session.identity.memberships[0].role.value == "owner"
    assert auth_service.check_readiness() is True

    with pytest.raises(RuntimeError, match="already exists"):
        auth_service.bootstrap_production_owner(
            email=owner_email,
            display_name="Production Owner",
            password=owner_password,
            organization_id="org-production",
            organization_name="Effortless Smoke Production",
            workspace_id="workspace-production",
            workspace_name="RecyclerOS Production",
        )

    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT event_type, details->>'role'
            FROM auth_audit_events
            WHERE user_id = %s AND event_type = 'account_bootstrapped'
            """,
            (user_id,),
        )
        audit_event = cursor.fetchone()

    assert audit_event == ("account_bootstrapped", "owner")


def test_operator_password_rotation_revokes_sessions_and_clears_lockout():
    import psycopg

    _reset_auth_state()
    auth_service = _runtime_auth(max_failures=2)
    auth_service.bootstrap_local_operator(OPERATOR_PASSWORD)
    session = auth_service.authenticate(OPERATOR_EMAIL, OPERATOR_PASSWORD)
    assert session is not None

    assert auth_service.authenticate(OPERATOR_EMAIL, "wrong-password") is None
    new_password = "rotated-postgres-runtime-password"
    revoked_sessions = auth_service.rotate_password(
        email=OPERATOR_EMAIL,
        password=new_password,
    )

    assert revoked_sessions == 1
    assert auth_service.resolve(session.access_token) is None
    assert auth_service.authenticate(OPERATOR_EMAIL, OPERATOR_PASSWORD) is None
    assert auth_service.authenticate(OPERATOR_EMAIL, new_password) is not None

    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM auth_login_attempts WHERE email = %s",
            (OPERATOR_EMAIL,),
        )
        attempts = cursor.fetchone()
        cursor.execute(
            """
            SELECT details->>'sessions_revoked'
            FROM auth_audit_events
            WHERE email = %s AND event_type = 'password_rotated'
            ORDER BY occurred_at DESC
            LIMIT 1
            """,
            (OPERATOR_EMAIL,),
        )
        audit_event = cursor.fetchone()

    assert attempts is None
    assert audit_event == ("1",)
