"""
Pydantic schemas for Interaction Event telemetry entity.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class InteractionEventCreate(BaseModel):
    student_id: int
    event_type: str = Field(..., json_schema_extra={"example": "editor_run_clicked"})
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    event_payload: Optional[str] = None


class InteractionEventResponse(InteractionEventCreate):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
