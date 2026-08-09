from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from auth import LocalAuthService, LocalUser, Role, TenantMembership
from main import create_app


MEMBERSHIP_BY_ROLE = {
    role: TenantMembership(
        organization_id="org-rbac",
        organization_name="RBAC Organization",
        workspace_id="workspace-rbac",
        workspace_name="RBAC Workspace",
        role=role,
    )
    for role in Role
}


@pytest.fixture()
def client():
    users = [
        LocalUser.from_password(
            user_id=f"user-{role.value}",
            email=f"{role.value}@example.com",
            display_name=f"{role.value.title()} User",
            password=f"{role.value}-password",
            memberships=(MEMBERSHIP_BY_ROLE[role],),
            password_iterations=1_000,
        )
        for role in Role
    ]
    outsider = LocalUser.from_password(
        user_id="user-outsider",
        email="outsider@example.com",
        display_name="Outside User",
        password="outsider-password",
        memberships=(
            TenantMembership(
                organization_id="org-outside",
                organization_name="Outside Organization",
                workspace_id="workspace-outside",
                workspace_name="Outside Workspace",
                role=Role.OWNER,
            ),
        ),
        password_iterations=1_000,
    )
    with TestClient(
        create_app(auth_service=LocalAuthService([*users, outsider]))
    ) as test_client:
        yield test_client


def _login(client, role: Role) -> dict[str, str]:
    response = client.post(
        "/v1/auth/login",
        json={
            "email": f"{role.value}@example.com",
            "password": f"{role.value}-password",
        },
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _tenant_headers(client, role: Role) -> dict[str, str]:
    return {
        **_login(client, role),
        "X-Organization-ID": "org-rbac",
        "X-Workspace-ID": "workspace-rbac",
    }


def test_login_returns_identity_membership_and_current_user(client):
    headers = _login(client, Role.OPERATOR)

    login = client.post(
        "/v1/auth/login",
        json={
            "email": "operator@example.com",
            "password": "operator-password",
        },
    )
    me = client.get("/v1/auth/me", headers=headers)

    assert login.json()["token_type"] == "bearer"
    assert login.json()["identity"]["memberships"][0]["role"] == "operator"
    assert me.status_code == 200
    assert me.json()["email"] == "operator@example.com"


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/v1/auth/login",
        json={"email": "operator@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_logout_revokes_local_session(client):
    headers = _login(client, Role.OPERATOR)

    logout = client.post("/v1/auth/logout", headers=headers)
    me = client.get("/v1/auth/me", headers=headers)

    assert logout.status_code == 204
    assert me.status_code == 401


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer invalid"},
    ],
)
def test_protected_endpoint_rejects_missing_or_invalid_token(client, headers):
    response = client.get(
        "/v1/opportunities",
        headers={
            **headers,
            "X-Organization-ID": "org-rbac",
            "X-Workspace-ID": "workspace-rbac",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_authenticated_user_cannot_claim_unassigned_tenant(client):
    response = client.get(
        "/v1/opportunities",
        headers={
            **_login(client, Role.OPERATOR),
            "X-Organization-ID": "org-outside",
            "X-Workspace-ID": "workspace-outside",
        },
    )

    assert response.status_code == 403
    assert "does not have access" in response.json()["detail"]


def test_viewer_can_read_but_cannot_operate_or_spoof_role(client):
    headers = {
        **_tenant_headers(client, Role.VIEWER),
        "X-Role": "owner",
    }

    read_response = client.get("/v1/opportunities", headers=headers)
    write_response = client.post(
        "/v1/opportunities",
        headers=headers,
        json={"title": "Viewer write attempt"},
    )

    assert read_response.status_code == 200
    assert write_response.status_code == 403
    assert "tenant:operate" in write_response.json()["detail"]


@pytest.mark.parametrize("role", [Role.OWNER, Role.ADMIN, Role.OPERATOR])
def test_operational_roles_can_create_opportunities(client, role):
    response = client.post(
        "/v1/opportunities",
        headers=_tenant_headers(client, role),
        json={"title": f"{role.value} opportunity"},
    )

    assert response.status_code == 201


def test_expired_session_is_rejected():
    current_time = datetime(2026, 7, 14, tzinfo=timezone.utc)

    def clock():
        return current_time

    user = LocalUser.from_password(
        user_id="user-expiring",
        email="expiring@example.com",
        display_name="Expiring User",
        password="expiring-password",
        memberships=(MEMBERSHIP_BY_ROLE[Role.OPERATOR],),
        password_iterations=1_000,
    )
    auth_service = LocalAuthService(
        [user],
        session_ttl=timedelta(seconds=0),
        clock=clock,
    )
    with TestClient(create_app(auth_service=auth_service)) as client:
        login = client.post(
            "/v1/auth/login",
            json={
                "email": "expiring@example.com",
                "password": "expiring-password",
            },
        )
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {login.json()['access_token']}"},
        )

    assert response.status_code == 401
    assert "expired" in response.json()["detail"]


def test_production_mode_requires_durable_runtime(monkeypatch):
    monkeypatch.setenv("RECYCLEROS_DEPLOYMENT_MODE", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="requires DATABASE_URL"):
        create_app()
