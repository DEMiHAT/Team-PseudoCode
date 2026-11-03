"""
Pydantic schemas for DSA coding problems and test case structures.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class TestCaseItem(BaseModel):
    id: int
    input: str
    expected_output: str
    is_hidden: bool = False
    explanation: Optional[str] = None


class ProblemSummary(BaseModel):
    id: int
    concept_id: int
    concept_code: Optional[str] = None
    title: str
    slug: str
    difficulty: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ProblemDetail(BaseModel):
    id: int
    concept_id: int
    title: str
    slug: str
    difficulty: str
    description_md: str
    starter_code_java: str
    sample_test_cases: List[TestCaseItem]
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
