"""
Pydantic schemas for Assessment entity.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AssessmentBase(BaseModel):
    subject_id: int
    title: str = Field(..., json_schema_extra={"example": "Unit 1 Formative Diagnostic"})
    assessment_type: str = Field(..., json_schema_extra={"example": "unit_formative"})
    total_points: float = 100.0
    time_limit_minutes: Optional[int] = None
    is_active: bool = True


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentResponse(AssessmentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

