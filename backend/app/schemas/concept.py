"""
Pydantic schemas for IT22301 concepts.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class ConceptResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    description: Optional[str] = None
    order_index: int
    model_config = ConfigDict(from_attributes=True)


class ConceptWithProblemCount(ConceptResponse):
    problem_count: int = 0
    current_mastery_p: Optional[float] = 0.20
