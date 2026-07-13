from dataclasses import dataclass
from typing import Any

from fastapi import Header, HTTPException, status


@dataclass(frozen=True)
class TenantContext:
    organization_id: str
    workspace_id: str


def require_tenant_context(
    x_organization_id: str | None = Header(default=None, alias="X-Organization-ID"),
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-ID"),
) -> TenantContext:
    if not x_organization_id or not x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Organization-ID and X-Workspace-ID headers are required.",
        )
    return TenantContext(organization_id=x_organization_id, workspace_id=x_workspace_id)


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
