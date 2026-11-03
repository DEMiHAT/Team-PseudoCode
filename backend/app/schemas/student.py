"""
Pydantic schemas for Student entity.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class StudentBase(BaseModel):
    external_id: str = Field(..., description="Unique university registration/roll ID", json_schema_extra={"example": "22IT045"})
    full_name: str = Field(..., description="Student full name", json_schema_extra={"example": "Aarav Sharma"})
    email: str = Field(..., description="Student email address", json_schema_extra={"example": "aarav.sharma@engineering.edu"})
    is_active: bool = Field(default=True)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

