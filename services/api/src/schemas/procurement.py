from typing import Literal

from pydantic import BaseModel


class ProcurementDecisionUpdate(BaseModel):
    organization_id: str | None = None
    workspace_id: str | None = None
    intent: Literal["resale", "personalUse", "partOut"]
