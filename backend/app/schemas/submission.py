"""
Submission schemas adapter.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CodeSubmissionRequest(BaseModel):
    learner_id: int = Field(default=1, description="Student ID submitting the code")
    problem_id: int = Field(..., description="Target Activity / Problem ID")
    code: str = Field(..., min_length=10, description="Java source code implementation")
    language: str = Field(default="java", description="Programming language")


class TestCaseResult(BaseModel):
    test_case_id: int
    passed: bool
    input: str
    expected_output: str
    actual_output: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class ExecutionResultResponse(BaseModel):
    status: str
    is_passed: bool
    test_cases_passed: int
    total_test_cases: int
    test_case_results: List[TestCaseResult]
    compile_error: Optional[str] = None
    runtime_error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    bkt_updated_mastery: Optional[float] = None
    triggered_intervention: Optional[Dict[str, Any]] = None


class SubmissionResponse(BaseModel):
    id: int
    learner_id: int
    problem_id: int
    status: str
    is_passed: bool
    test_cases_passed: int
    total_test_cases: int
    execution_time_ms: Optional[float] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

