from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_store
from store import InMemoryStore
from tenant import TenantContext, require_tenant_context

router = APIRouter()


@router.get("/{opportunity_id}/analysis")
def get_procurement_analysis(
    opportunity_id: str,
    tenant: TenantContext = Depends(require_tenant_context),
    store: InMemoryStore = Depends(get_store),
):
    analysis = store.get_or_create_procurement_analysis(opportunity_id, tenant)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found in tenant workspace.",
        )
    return analysis
