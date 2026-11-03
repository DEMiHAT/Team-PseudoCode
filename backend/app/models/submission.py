"""
Submission / Attempt model recording code evaluations and execution metrics.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Submission(Base):
    """
    Records a student's Java code submission and evaluation metrics from Judge0.
    """

    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(20), default="java", nullable=False)
    status = Column(String(50), nullable=False)  # Accepted, Wrong Answer, Compilation Error, Time Limit Exceeded
    execution_time_ms = Column(Float, nullable=True)
    memory_kb = Column(Float, nullable=True)
    is_passed = Column(Boolean, default=False, nullable=False)
    test_cases_passed = Column(Integer, default=0, nullable=False)
    total_test_cases = Column(Integer, default=0, nullable=False)
    output_log = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    learner = relationship("Learner", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")

    def __repr__(self):
        return f"<Submission id={self.id} learner={self.learner_id} passed={self.is_passed}>"
