"""
Pydantic schemas for Prerequisite dependency edges.
"""

from pydantic import BaseModel, Field, ConfigDict


class PrerequisiteBase(BaseModel):
    topic_id: int = Field(..., description="Target dependent topic ID")
    prerequisite_topic_id: int = Field(..., description="Required prerequisite topic ID")
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    is_mandatory: bool = True


class PrerequisiteCreate(PrerequisiteBase):
    pass


class PrerequisiteResponse(PrerequisiteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

