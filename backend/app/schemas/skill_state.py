"""
Pydantic schemas for Learner Skill State.
Maintains concept-level multidimensional mastery and evidence tracking.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SkillStateBase(BaseModel):
    student_id: int
    topic_id: int
    p_known: float = Field(default=0.20, ge=0.0, le=1.0, description="BKT latent cognitive mastery belief")
    p_learn: float = Field(default=0.15, ge=0.0, le=1.0)
    p_guess: float = Field(default=0.15, ge=0.0, le=1.0)
    p_slip: float = Field(default=0.10, ge=0.0, le=1.0)
    conceptual_mastery: float = Field(default=0.0, ge=0.0, le=1.0, description="Conceptual assessment score")
    practical_mastery: float = Field(default=0.0, ge=0.0, le=1.0, description="Hands-on coding implementation score")
    independent_success_count: int = Field(default=0, ge=0, description="Solved without hints or scaffolding")
    assisted_success_count: int = Field(default=0, ge=0, description="Solved with scaffolding assistance")
    consecutive_failures: int = Field(default=0, ge=0)
    total_attempts: int = Field(default=0, ge=0)


class SkillStateCreate(BaseModel):
    student_id: int
    topic_id: int
    p_known: float = 0.20
    p_learn: float = 0.15
    p_guess: float = 0.15
    p_slip: float = 0.10
    conceptual_mastery: float = 0.0
    practical_mastery: float = 0.0


class SkillStateUpdate(BaseModel):
    p_known: float
    conceptual_mastery: float
    practical_mastery: float
    is_correct: bool
    was_assisted: bool


class SkillStateResponse(SkillStateBase):
    id: int
    last_evaluated_at: datetime

    model_config = ConfigDict(from_attributes=True)

