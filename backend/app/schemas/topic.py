"""
Pydantic schemas for Topic entity.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TopicBase(BaseModel):
    unit_id: int
    code: str = Field(..., json_schema_extra={"example": "IT22301-U1-SLL"})
    name: str = Field(..., json_schema_extra={"example": "Singly Linked List Reversal"})
    description: Optional[str] = None
    difficulty_level: str = Field(default="Intermediate", json_schema_extra={"example": "Intermediate"})
    order_index: int = 0


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

