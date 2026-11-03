"""
Pydantic schemas for Subject entity.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SubjectBase(BaseModel):
    code: str = Field(..., description="Subject code", json_schema_extra={"example": "IT22301"})
    name: str = Field(..., description="Subject title", json_schema_extra={"example": "Data Structures and Algorithms"})
    description: Optional[str] = None
    is_active: bool = True


class SubjectCreate(SubjectBase):
    pass


class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
