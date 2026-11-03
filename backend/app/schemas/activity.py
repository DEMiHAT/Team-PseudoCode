"""
Pydantic schemas for Activity entity.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ActivityBase(BaseModel):
    topic_id: int
    title: str = Field(..., json_schema_extra={"example": "Reverse Singly Linked List"})
    slug: str = Field(..., json_schema_extra={"example": "reverse-singly-linked-list"})
    activity_type: str = Field(..., json_schema_extra={"example": "coding_exercise"})
    description_md: str
    difficulty: str = Field(default="Medium")
    starter_template: Optional[str] = None
    solution_reference: Optional[str] = None
    test_cases_json: Optional[str] = None
    is_active: bool = True


class ActivityCreate(ActivityBase):
    pass


class ActivityResponse(ActivityBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
