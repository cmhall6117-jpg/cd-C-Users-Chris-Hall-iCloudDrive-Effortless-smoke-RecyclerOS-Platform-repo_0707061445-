from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_store
from store import InMemoryStore
from tenant import TenantContext, require_tenant_context

router = APIRouter()


@router.post("/focus-point/start", status_code=status.HTTP_201_CREATED)
def start_focus_point(
    vehicle_id: str,
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    session = store.start_harvest_session(vehicle_id, tenant)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in tenant workspace.",
        )
    return session


@router.post("/focus-point/complete")
def complete_focus_point(
    harvest_session_id: str,
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    session = store.complete_harvest_session(harvest_session_id, tenant)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Harvest session not found in tenant workspace.",
        )
    return session
