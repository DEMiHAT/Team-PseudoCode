"""
Learner schemas adapter bridging Student entities to client profile format.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.student import StudentBase


class LearnerBase(StudentBase):
    pass


class LearnerCreate(LearnerBase):
    pass


class LearnerResponse(BaseModel):
    id: int
    student_id: str
    full_name: str
    email: str
    semester: int = 3
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

