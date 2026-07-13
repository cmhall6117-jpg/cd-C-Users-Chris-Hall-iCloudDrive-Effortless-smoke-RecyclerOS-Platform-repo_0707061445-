from fastapi import APIRouter, Depends
from tenant import TenantContext, require_tenant_context

router = APIRouter()

@router.get("/{opportunity_id}/analysis")
def get_procurement_analysis(opportunity_id: str, tenant: TenantContext = Depends(require_tenant_context)):
    return {
        "organization_id": tenant.organization_id,
        "workspace_id": tenant.workspace_id,
        "opportunity_id": opportunity_id,
        "auction_access_type": "nonDealerPublic",
        "recommended_intent": "partOut",
        "scenarios": [
            {"intent": "resale", "projected_revenue": 9500, "projected_costs": 7550, "recommended_max_bid": 4800, "projected_net_profit": 1950, "projected_margin_percent": 20.5, "confidence_score": 72},
            {"intent": "personalUse", "projected_revenue": 0, "projected_costs": 5300, "recommended_max_bid": 5300, "projected_net_profit": 0, "projected_margin_percent": 0, "confidence_score": 65},
            {"intent": "partOut", "projected_revenue": 8500, "projected_costs": 5250, "recommended_max_bid": 3900, "projected_net_profit": 3250, "projected_margin_percent": 38.2, "confidence_score": 81}
        ]
    }
