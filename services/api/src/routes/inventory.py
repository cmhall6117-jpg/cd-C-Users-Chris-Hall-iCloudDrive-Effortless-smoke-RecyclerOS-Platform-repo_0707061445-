from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tenant import TenantContext, require_tenant_context, validate_payload_tenant

router = APIRouter()

class InventoryCreate(BaseModel):
    organization_id: str | None = None
    workspace_id: str | None = None
    part_name: str
    source_vehicle_id: str | None = None
    harvest_session_id: str | None = None
    storage_location_id: str | None = None
    condition: str = "usedUntested"
    status: str = "available"
    quantity: int = 1
    estimated_value: float | None = None

@router.post("")
def create_inventory_item(payload: InventoryCreate, tenant: TenantContext = Depends(require_tenant_context)):
    validate_payload_tenant(payload, tenant)
    now = datetime.now(timezone.utc)
    return {
        "inventory_item_id": "INV-DEMO-000001",
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "inventory_code": "INV-000001",
        "part_name": payload.part_name,
        "condition": payload.condition,
        "status": payload.status,
        "quantity": payload.quantity,
        "created_at": now.isoformat(),
        "event_created": "inventory.created"
    }

@router.get("")
def list_inventory_items(tenant: TenantContext = Depends(require_tenant_context)):
    return {
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "items": [
            {
                "inventory_item_id": "INV-DEMO-000001",
                "inventory_code": "INV-000001",
                "part_name": "ECM / PCM",
                "condition": "usedUntested",
                "status": "available",
                "quantity": 1
            }
        ]
    }
