"""
Pydantic schemas for Code Submission entity.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CodeSubmissionCreate(BaseModel):
    attempt_id: int
    student_id: int
    activity_id: int
    source_code: str = Field(..., min_length=5)
    language: str = Field(default="java")


class CodeSubmissionResponse(BaseModel):
    id: int
    attempt_id: int
    student_id: int
    activity_id: int
    source_code: str
    language: str
    submission_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

