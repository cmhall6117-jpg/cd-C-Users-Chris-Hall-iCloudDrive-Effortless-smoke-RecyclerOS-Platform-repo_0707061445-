from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth import (
    ROLE_PERMISSIONS,
    AuthService,
    AuthenticatedIdentity,
    Permission,
    Role,
)
from auth_dependencies import get_auth_service

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class TenantContext:
    organization_id: str
    workspace_id: str
    user_id: str
    email: str
    role: Role
    permissions: frozenset[Permission]


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_identity(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedIdentity:
    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise _unauthorized("Bearer authentication is required.")
    identity = auth_service.resolve(credentials.credentials)
    if identity is None:
        raise _unauthorized("Bearer token is invalid or expired.")
    return identity


def require_tenant_context(
    x_organization_id: str | None = Header(default=None, alias="X-Organization-ID"),
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-ID"),
    identity: AuthenticatedIdentity = Depends(require_identity),
) -> TenantContext:
    if not x_organization_id or not x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Organization-ID and X-Workspace-ID headers are required.",
        )

    membership = next(
        (
            item
            for item in identity.memberships
            if item.organization_id == x_organization_id
            and item.workspace_id == x_workspace_id
        ),
        None,
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated user does not have access to the tenant workspace.",
        )

    return TenantContext(
        organization_id=x_organization_id,
        workspace_id=x_workspace_id,
        user_id=identity.user_id,
        email=identity.email,
        role=membership.role,
        permissions=ROLE_PERMISSIONS[membership.role],
    )


def require_permission(
    permission: Permission,
) -> Callable[..., TenantContext]:
    def dependency(
        tenant: TenantContext = Depends(require_tenant_context),
    ) -> TenantContext:
        if permission not in tenant.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{tenant.role.value}' lacks '{permission.value}'.",
            )
        return tenant

    return dependency


def validate_payload_tenant(payload: Any, tenant: TenantContext) -> None:
    organization_id = getattr(payload, "organization_id", None)
    workspace_id = getattr(payload, "workspace_id", None)
    if organization_id is not None and organization_id != tenant.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payload organization_id does not match tenant context.",
        )
    if workspace_id is not None and workspace_id != tenant.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payload workspace_id does not match tenant context.",
        )
