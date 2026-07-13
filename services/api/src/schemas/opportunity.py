from pydantic import BaseModel, Field
from typing import Optional

class OpportunityCreate(BaseModel):
    title: str = Field(min_length=1)
    source_type: str = "manual"
    procurement_intent: str = "undecided"
    vin: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
