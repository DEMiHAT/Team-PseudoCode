"""
Pydantic schemas for Attempt entity.
Tracks student encounters with independent problem-solving flags.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AttemptBase(BaseModel):
    student_id: int
    activity_id: Optional[int] = None
    assessment_id: Optional[int] = None
    attempt_number: int = Field(default=1, ge=1)
    is_correct: bool
    score: float = 0.0
    was_assisted: bool = Field(default=False, description="Whether the student used hints or scaffolding")
    scaffolding_level_accessed: int = Field(default=0, ge=0, le=4, description="0 = independent, 1-4 = scaffolding tier")
    time_spent_seconds: Optional[int] = None


class AttemptCreate(AttemptBase):
    pass


class AttemptResponse(AttemptBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
