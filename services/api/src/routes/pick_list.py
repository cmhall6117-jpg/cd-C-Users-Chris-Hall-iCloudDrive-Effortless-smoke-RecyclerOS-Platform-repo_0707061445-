from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_store
from schemas.pick_list import PickListAvailabilityUpdate, PickListItemCreate
from store import InMemoryStore
from tenant import TenantContext, require_tenant_context, validate_payload_tenant

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_pick_list_item(
    payload: PickListItemCreate,
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    validate_payload_tenant(payload, tenant)
    values = payload.model_dump(exclude={"organization_id", "workspace_id"})
    item = store.create_pick_list_item(tenant, values)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in tenant workspace.",
        )
    return item


@router.get("")
def list_pick_list_items(
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    return {
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "items": store.list_pick_list_items(tenant),
    }


@router.patch("/{pick_list_item_id}/availability")
def update_pick_list_availability(
    pick_list_item_id: str,
    payload: PickListAvailabilityUpdate,
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    validate_payload_tenant(payload, tenant)
    item = store.update_pick_list_availability(
        pick_list_item_id,
        payload.availability_status,
        tenant,
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pick-list item not found in tenant workspace.",
        )
    return item
