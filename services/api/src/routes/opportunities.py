from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tenant import TenantContext, require_tenant_context, validate_payload_tenant

router = APIRouter()

class OpportunityCreate(BaseModel):
    title: str
    procurement_intent: str = "undecided"
    source_type: str = "manual"
    organization_id: str | None = None
    workspace_id: str | None = None

@router.post("")
def create_opportunity(payload: OpportunityCreate, tenant: TenantContext = Depends(require_tenant_context)):
    validate_payload_tenant(payload, tenant)
    return {
        "opportunity_id": "OPP-DEMO-000001",
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "title": payload.title,
        "procurement_intent": payload.procurement_intent,
        "source_type": payload.source_type,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "event_created": "EVT-001 Opportunity Discovered",
    }

@router.get("")
def list_opportunities(tenant: TenantContext = Depends(require_tenant_context)):
    return {
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "items": [],
        "message": "Opportunity listing scaffold ready.",
    }
