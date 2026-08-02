from pydantic import BaseModel, Field

class OpportunityCreate(BaseModel):
    organization_id: str | None = None
    workspace_id: str | None = None
    title: str = Field(min_length=1)
    source_type: str = "manual"
    procurement_intent: str = "undecided"
    vin: str | None = None
    year: int | None = Field(default=None, ge=1886, le=2100)
    make: str | None = None
    model: str | None = None
    estimated_max_bid: float | None = Field(default=None, ge=0)
    estimated_net_profit: float | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=100)
