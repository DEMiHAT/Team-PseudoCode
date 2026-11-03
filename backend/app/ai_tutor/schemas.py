"""
Data Structures & Algorithms (IT22301) AI Tutoring Schemas.
Pydantic contracts for context representation, pedagogical requests, and validated responses.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CodeExecutionEvidence(BaseModel):
    """Execution evidence from sandbox / Judge0 test runner."""
    has_evidence: bool = Field(default=False, description="True if code was actually executed")
    status: Optional[str] = Field(default=None, description="Compilation Error, Runtime Error, Wrong Answer, Accepted")
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    failed_test_case: Optional[Dict[str, Any]] = None


class TutorContext(BaseModel):
    """
    Comprehensive context bundle required by the AI tutor.
    Contains curricular location, cognitive state, code, and execution evidence.
    """
    student_id: int
    subject: str = Field(default="IT22301 – Data Structures and Algorithms")
    unit: str = Field(default="Unit 2: Linear Data Structures")
    topic: str = Field(default="Stacks")
    subtopic: Optional[str] = Field(default="Array Implementation and Boundary Conditions")
    estimated_mastery: Dict[str, float] = Field(default_factory=dict, description="Skill name to probability mapping")
    mastery_level_label: str = Field(default="Developing", description="Novice, Developing, Competent, Mastered")
    previous_errors: List[str] = Field(default_factory=list, description="Recent error logs")
    previous_assistance: List[str] = Field(default_factory=list, description="Recent scaffolding interventions")
    scaffold_level: int = Field(default=1, ge=0, le=5, description="Scaffolding tier L0 to L5")
    current_code: str = Field(default="", description="Student Java code")
    execution_evidence: CodeExecutionEvidence = Field(default_factory=CodeExecutionEvidence)
    confirmed_misconceptions: List[str] = Field(default_factory=list, description="Recurrent diagnosed misconceptions")
    candidate_misconceptions: List[str] = Field(default_factory=list, description="Unconfirmed single-occurrence slips")


class TutorResponse(BaseModel):
    """Standardized validated response produced by AI tutoring interfaces."""
    success: bool
    is_fallback: bool
    content: str
    actionable_next_step: Optional[str] = None
    scaffold_level: int
    pedagogical_strategy: str
    fallback_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HintRequest(BaseModel):
    """Request payload for Socratic hint generation."""
    student_id: int
    topic_id: Optional[int] = None
    activity_id: Optional[int] = None
    scaffold_level: Optional[int] = Field(default=None, ge=0, le=5)
    current_code: str
    execution_status: Optional[str] = None
    compiler_error: Optional[str] = None
    runtime_error: Optional[str] = None
    failing_input: Optional[str] = None


class ErrorExplanationRequest(BaseModel):
    """Request payload for code error explanation."""
    student_id: int
    topic_id: Optional[int] = None
    activity_id: Optional[int] = None
    code: str
    compiler_error: Optional[str] = None
    runtime_error: Optional[str] = None
    failing_test_details: Optional[Dict[str, Any]] = None


class ConceptSimplificationRequest(BaseModel):
    """Request payload for simplifying a complex DSA concept."""
    student_id: int
    concept_name: str
    student_question: Optional[str] = None
    target_analogy_domain: Optional[str] = Field(default="everyday_real_world")


class PracticeOption(BaseModel):
    id: str
    text: str


class PracticeQuestionItem(BaseModel):
    question_id: str
    prompt: str
    options: List[PracticeOption]
    correct_option_id: str
    explanation: str
    target_skill: str
    difficulty: str  # Beginner, Intermediate, Advanced
    sample_code_snippet: Optional[str] = None


class PracticeQuestionRequest(BaseModel):
    """Request payload for generating personalized practice questions."""
    student_id: int
    topic_id: Optional[int] = None
    target_concept: Optional[str] = None
    difficulty: Optional[str] = Field(default="Intermediate")
    count: int = Field(default=1, ge=1, le=5)


class PracticeQuestionResponse(BaseModel):
    success: bool
    is_fallback: bool
    target_concept: str
    questions: List[PracticeQuestionItem]
    fallback_reason: Optional[str] = None

