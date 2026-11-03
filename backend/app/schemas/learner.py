"""
Pydantic schemas for learner entities and profile management.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class LearnerBase(BaseModel):
    student_id: str = Field(..., description="College student registration ID", json_schema_extra={"example": "22IT045"})
    full_name: str = Field(..., description="Student full name", json_schema_extra={"example": "Aarav Sharma"})
    email: str = Field(..., description="Student email address", json_schema_extra={"example": "aarav.s@college.edu"})
    semester: int = Field(default=3, ge=1, le=8)


class LearnerCreate(LearnerBase):
    pass


class LearnerResponse(LearnerBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConceptMasterySummary(BaseModel):
    concept_id: int
    concept_code: str
    concept_name: str
    category: str
    p_known: float
    mastery_percentage: float
    total_attempts: int
    successful_attempts: int


class LearnerProfileResponse(BaseModel):
    learner: LearnerResponse
    mastery_overview: List[ConceptMasterySummary]
    overall_mastery_index: float
