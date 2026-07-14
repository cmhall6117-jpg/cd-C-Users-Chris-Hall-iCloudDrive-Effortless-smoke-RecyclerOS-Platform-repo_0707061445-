from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    organization_id: str | None = None
    workspace_id: str | None = None
    part_name: str = Field(min_length=1)
    source_vehicle_id: str | None = None
    harvest_session_id: str | None = None
    storage_location_id: str | None = None
    condition: str = "usedUntested"
    status: str = "available"
    quantity: int = Field(default=1, ge=1)
    estimated_value: float | None = Field(default=None, ge=0)
