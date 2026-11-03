"""
Pydantic schemas for Unit entity.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UnitBase(BaseModel):
    subject_id: int
    unit_number: int = Field(..., ge=1)
    title: str = Field(..., json_schema_extra={"example": "Unit 1: Linear Collections"})
    description: Optional[str] = None
    order_index: int = 0


class UnitCreate(UnitBase):
    pass


class UnitResponse(UnitBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
