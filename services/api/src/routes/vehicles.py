from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_store
from schemas.vehicle import VehicleCreate
from store import InMemoryStore
from tenant import TenantContext, require_tenant_context, validate_payload_tenant

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    validate_payload_tenant(payload, tenant)
    values = payload.model_dump(exclude={"organization_id", "workspace_id"})
    vehicle = store.create_vehicle(tenant, values)
    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked opportunity not found in tenant workspace.",
        )
    return vehicle


@router.get("/{vehicle_code}")
def get_vehicle(
    vehicle_code: str,
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    vehicle = store.get_vehicle(vehicle_code, tenant)
    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in tenant workspace.",
        )
    return vehicle
