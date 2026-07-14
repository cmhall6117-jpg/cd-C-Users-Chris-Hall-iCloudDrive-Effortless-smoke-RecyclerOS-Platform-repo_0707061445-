from fastapi import APIRouter, Depends, HTTPException, status

from auth import Permission
from dependencies import get_store
from store import WorkflowStore
from tenant import TenantContext, require_permission

router = APIRouter()


@router.get("/{opportunity_id}/analysis")
def get_procurement_analysis(
    opportunity_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.READ)),
    store: WorkflowStore = Depends(get_store),
):
    analysis = store.get_or_create_procurement_analysis(opportunity_id, tenant)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found in tenant workspace.",
        )
    return analysis
