from fastapi import APIRouter, Depends, HTTPException, status

from auth import Permission
from dependencies import get_store
from schemas.opportunity import OpportunityCreate
from store import InMemoryStore
from tenant import TenantContext, require_permission, validate_payload_tenant

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityCreate,
    tenant: TenantContext = Depends(require_permission(Permission.OPERATE)),
    store: InMemoryStore = Depends(get_store),
):
    validate_payload_tenant(payload, tenant)
    values = payload.model_dump(exclude={"organization_id", "workspace_id"})
    return store.create_opportunity(tenant, values)


@router.get("")
def list_opportunities(
    tenant: TenantContext = Depends(require_permission(Permission.READ)),
    store: InMemoryStore = Depends(get_store),
):
    return {
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "items": store.list_opportunities(tenant),
    }


@router.get("/{opportunity_id}")
def get_opportunity(
    opportunity_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.READ)),
    store: InMemoryStore = Depends(get_store),
):
    opportunity = store.get_opportunity(opportunity_id, tenant)
    if opportunity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found in tenant workspace.",
        )
    return opportunity
