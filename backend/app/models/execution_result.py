"""
Execution Result database model.
Captures compiler and runtime sandbox telemetry (e.g., from Judge0 CE).
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ExecutionResult(Base):
    """
    Physical execution outcome of a code submission inside the sandboxed test harness.
    """

    __tablename__ = "execution_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code_submission_id = Column(Integer, ForeignKey("code_submissions.id", ondelete="CASCADE"), nullable=False, index=True)

    status = Column(String(50), nullable=False)  # 'Accepted', 'Wrong Answer', 'Compilation Error', 'Runtime Error'
    is_passed = Column(Boolean, nullable=False)
    tests_passed = Column(Integer, default=0, nullable=False)
    total_tests = Column(Integer, default=0, nullable=False)

    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    compiler_output = Column(Text, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    memory_kb = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    submission = relationship("CodeSubmission", back_populates="execution_results")

    def __repr__(self):
        return f"<ExecutionResult id={self.id} status='{self.status}' passed={self.is_passed} time={self.execution_time_ms}ms>"
