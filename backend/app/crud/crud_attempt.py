"""
CRUD operations for Attempt, CodeSubmission, and ExecutionResult entities.
Captures complete evidence trails for independent and assisted problem-solving.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.attempt import Attempt
from app.models.code_submission import CodeSubmission
from app.models.execution_result import ExecutionResult
from app.schemas.attempt import AttemptCreate, AttemptBase
from app.schemas.code_submission import CodeSubmissionCreate
from app.schemas.execution_result import ExecutionResultCreate


class CRUDAttempt(CRUDBase[Attempt, AttemptCreate, AttemptBase]):
    def get_by_student_and_activity(
        self, db: Session, *, student_id: int, activity_id: int
    ) -> List[Attempt]:
        return (
            db.query(Attempt)
            .filter(Attempt.student_id == student_id, Attempt.activity_id == activity_id)
            .order_by(Attempt.attempt_number.desc())
            .all()
        )

    def count_consecutive_failures(
        self, db: Session, *, student_id: int, activity_id: int
    ) -> int:
        """Counts recent consecutive failures on an activity."""
        recent_attempts = (
            db.query(Attempt)
            .filter(Attempt.student_id == student_id, Attempt.activity_id == activity_id)
            .order_by(Attempt.started_at.desc())
            .limit(10)
            .all()
        )
        failures = 0
        for att in recent_attempts:
            if not att.is_correct:
                failures += 1
            else:
                break
        return failures


class CRUDCodeSubmission(CRUDBase[CodeSubmission, CodeSubmissionCreate, CodeSubmissionCreate]):
    def get_by_attempt(self, db: Session, *, attempt_id: int) -> List[CodeSubmission]:
        return db.query(CodeSubmission).filter(CodeSubmission.attempt_id == attempt_id).all()


class CRUDExecutionResult(CRUDBase[ExecutionResult, ExecutionResultCreate, ExecutionResultCreate]):
    def get_by_submission(
        self, db: Session, *, code_submission_id: int
    ) -> List[ExecutionResult]:
        return (
            db.query(ExecutionResult)
            .filter(ExecutionResult.code_submission_id == code_submission_id)
            .all()
        )


attempt = CRUDAttempt(Attempt)
code_submission = CRUDCodeSubmission(CodeSubmission)
execution_result = CRUDExecutionResult(ExecutionResult)

