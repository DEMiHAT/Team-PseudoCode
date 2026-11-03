"""
Pydantic schemas for Intervention entity.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class InterventionBase(BaseModel):
    student_id: int
    topic_id: int
    activity_id: Optional[int] = None
    attempt_id: Optional[int] = None
    intervention_type: str = Field(..., json_schema_extra={"example": "socratic_hint"})
    scaffolding_tier: int = Field(default=1, ge=1, le=4)
    trigger_reason: str = Field(..., json_schema_extra={"example": "off_by_one_detected"})
    hint_content: str
    is_llm_generated: bool = False
    subsequent_attempt_successful: Optional[bool] = None


class InterventionCreate(InterventionBase):
    pass


class InterventionResponse(InterventionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
