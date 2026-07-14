from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_store
from schemas.inventory import InventoryCreate
from store import InMemoryStore
from tenant import TenantContext, require_tenant_context, validate_payload_tenant

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: InventoryCreate,
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    validate_payload_tenant(payload, tenant)
    values = payload.model_dump(exclude={"organization_id", "workspace_id"})
    item = store.create_inventory_item(tenant, values)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked vehicle or harvest session not found in tenant workspace.",
        )
    return item


@router.get("")
def list_inventory_items(
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    return {
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "items": store.list_inventory_items(tenant),
    }
