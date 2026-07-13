from datetime import datetime, timezone
from fastapi import APIRouter
from schemas.opportunity import OpportunityCreate

router = APIRouter()

@router.post("")
def create_opportunity(payload: OpportunityCreate):
    now = datetime.now(timezone.utc)
    return {
        "opportunity_id": "OPP-DEMO-000001",
        "opportunity_code": "OPP-000001",
        "title": payload.title,
        "source_type": payload.source_type,
        "procurement_intent": payload.procurement_intent,
        "status": "discovered",
        "vin": payload.vin,
        "year": payload.year,
        "make": payload.make,
        "model": payload.model,
        "created_at": now.isoformat(),
        "event_created": {
            "event_type": "opportunity.discovered",
            "event_code": "EVT-DEMO-000001"
        }
    }

@router.get("")
def list_opportunities():
    return {
        "items": [
            {
                "opportunity_id": "OPP-DEMO-000001",
                "opportunity_code": "OPP-000001",
                "title": "2019 Ford F-150 Auction Lead",
                "source_type": "nonDealerAuction",
                "procurement_intent": "partOut",
                "status": "discovered"
            }
        ]
    }
