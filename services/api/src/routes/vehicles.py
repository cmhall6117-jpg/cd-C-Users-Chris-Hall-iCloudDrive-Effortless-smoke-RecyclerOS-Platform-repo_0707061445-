from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from schemas.vehicle import VehicleCreate
from tenant import TenantContext, require_tenant_context, validate_payload_tenant

router = APIRouter()

@router.post("")
def create_vehicle(payload: VehicleCreate, tenant: TenantContext = Depends(require_tenant_context)):
    validate_payload_tenant(payload, tenant)
    now = datetime.now(timezone.utc)
    return {
        "vehicle_id": "VEH-DEMO-000001",
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "vehicle_code": "VEH-000001",
        "vin": payload.vin,
        "year": payload.year,
        "make": payload.make,
        "model": payload.model,
        "lifecycle_status": "discovered",
        "created_at": now.isoformat(),
        "event_created": {
            "event_type": "vehicle.evaluated",
            "event_code": "EVT-DEMO-000002"
        }
    }

@router.get("/{vehicle_code}")
def get_vehicle(vehicle_code: str, tenant: TenantContext = Depends(require_tenant_context)):
    return {
        "vehicle_id": "VEH-DEMO-000001",
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "vehicle_code": vehicle_code,
        "vin": "DEMO-VIN-PENDING",
        "year": 2019,
        "make": "Ford",
        "model": "F-150",
        "lifecycle_status": "activeHarvest",
        "timeline": [
            {"event_type": "opportunity.discovered", "title": "Opportunity Discovered"},
            {"event_type": "vehicle.evaluated", "title": "Vehicle Evaluated"},
            {"event_type": "vehicle.received", "title": "Vehicle Received"}
        ]
    }
