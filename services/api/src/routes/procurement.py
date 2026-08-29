from fastapi import APIRouter, Depends, HTTPException, status

from auth import Permission
from dependencies import get_store
from schemas.procurement import ProcurementDecisionUpdate
from store import WorkflowStore
from tenant import TenantContext, require_permission, validate_payload_tenant

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


@router.patch("/{opportunity_id}/decision")
def update_procurement_decision(
    opportunity_id: str,
    payload: ProcurementDecisionUpdate,
    tenant: TenantContext = Depends(require_permission(Permission.OPERATE)),
    store: WorkflowStore = Depends(get_store),
):
    validate_payload_tenant(payload, tenant)
    opportunity = store.update_procurement_intent(
        opportunity_id,
        payload.intent,
        tenant,
    )
    if opportunity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found in tenant workspace.",
        )
    return opportunity
