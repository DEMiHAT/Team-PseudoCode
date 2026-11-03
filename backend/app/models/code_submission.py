"""
Code Submission database model.
Dedicated record of practical programming implementation evidence.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class CodeSubmission(Base):
    """
    Practical programming submission for a coding activity.
    Preserves exact student implementation artifacts and feeds into sandboxed execution.
    """

    __tablename__ = "code_submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)

    source_code = Column(Text, nullable=False)
    language = Column(String(30), default="java", nullable=False)
    submission_timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    attempt = relationship("Attempt", back_populates="code_submissions")
    student = relationship("Student", back_populates="code_submissions")
    activity = relationship("Activity", back_populates="code_submissions")
    execution_results = relationship("ExecutionResult", back_populates="submission", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CodeSubmission id={self.id} student={self.student_id} activity={self.activity_id} lang='{self.language}'>"
