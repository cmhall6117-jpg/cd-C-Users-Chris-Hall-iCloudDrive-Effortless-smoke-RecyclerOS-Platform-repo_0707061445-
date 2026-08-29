from datetime import datetime

from pydantic import BaseModel, Field

class VehicleCreate(BaseModel):
    organization_id: str | None = None
    workspace_id: str | None = None
    opportunity_id: str | None = None
    vin: str | None = None
    year: int | None = Field(default=None, ge=1886, le=2100)
    make: str | None = None
    model: str | None = None
    trim: str | None = None
    engine: str | None = None
    transmission: str | None = None
    drivetrain: str | None = None
    mileage: int | None = Field(default=None, ge=0)


class VehicleMileageUpdate(BaseModel):
    organization_id: str | None = None
    workspace_id: str | None = None
    mileage: int = Field(ge=0)


class VehicleRead(BaseModel):
    vehicle_id: str
    vehicle_code: str
    vin: str | None
    year: int | None
    make: str | None
    model: str | None
    lifecycle_status: str
    created_at: datetime
