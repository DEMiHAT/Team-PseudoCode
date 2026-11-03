"""
Pydantic schemas for the Cognitive Intelligence Engine: BKT, Scaffolding, and Misconception Diagnosis.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BKTUpdateRequest(BaseModel):
    learner_id: int
    concept_id: int
    is_correct: bool


class BKTStateResponse(BaseModel):
    learner_id: int
    concept_id: int
    prior_p_known: float
    posterior_p_known: float
    next_prior_p_known: float
    mastery_percentage: float
    is_mastered: bool  # Typically p_known >= 0.85


class ScaffoldingRequest(BaseModel):
    learner_id: int
    problem_id: int
    current_code: str
    requested_level: Optional[int] = Field(default=None, ge=1, le=4)
    compiler_error: Optional[str] = None
    failing_test_input: Optional[str] = None


class ScaffoldingHintResponse(BaseModel):
    level: int  # 1: Concept, 2: Algorithmic Logic, 3: State Trace, 4: Skeleton / Fix
    title: str
    hint_text: str
    code_snippet: Optional[str] = None
    is_llm_generated: bool
    pedagogical_strategy: str


class DiagnosisRequest(BaseModel):
    code: str
    problem_id: int
    compiler_error: Optional[str] = None
    failing_test_input: Optional[str] = None


class MisconceptionItem(BaseModel):
    rule_code: str
    name: str
    severity: str  # Critical, Warning, LogicError
    explanation: str
    suggested_remedy: str


class DiagnosisResponse(BaseModel):
    misconceptions_detected: List[MisconceptionItem]
    detected_count: int
    recommended_scaffolding_tier: int

