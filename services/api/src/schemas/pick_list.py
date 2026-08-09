from typing import Literal

from pydantic import BaseModel, Field


class PickListItemCreate(BaseModel):
    organization_id: str | None = None
    workspace_id: str | None = None
    vehicle_id: str
    yard_name: str = Field(min_length=1)
    yard_row: str | None = None
    availability_status: Literal["pending", "available", "unavailable"] = "pending"


class PickListAvailabilityUpdate(BaseModel):
    organization_id: str | None = None
    workspace_id: str | None = None
    availability_status: Literal["pending", "available", "unavailable"]
