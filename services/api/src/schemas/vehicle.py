from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VehicleCreate(BaseModel):
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    vin: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    engine: Optional[str] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    mileage: Optional[int] = None

class VehicleRead(BaseModel):
    vehicle_id: str
    vehicle_code: str
    vin: Optional[str]
    year: Optional[int]
    make: Optional[str]
    model: Optional[str]
    lifecycle_status: str
    created_at: datetime
