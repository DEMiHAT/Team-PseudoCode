"""
Pydantic schemas for Execution Result entity.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ExecutionResultCreate(BaseModel):
    code_submission_id: int
    status: str
    is_passed: bool
    tests_passed: int = 0
    total_tests: int = 0
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compiler_output: Optional[str] = None
    execution_time_ms: Optional[float] = None
    memory_kb: Optional[float] = None


class ExecutionResultResponse(ExecutionResultCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

