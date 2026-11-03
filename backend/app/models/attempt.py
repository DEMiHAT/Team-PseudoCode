"""
Attempt database model.
Tracks discrete student problem-solving encounters, noting whether hints or scaffolding were used.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Attempt(Base):
    """
    Records an individual student attempt on an activity or assessment.
    Crucially records `was_assisted` and `scaffolding_level_accessed` to differentiate
    independent mastery from scaffolded success.
    """

    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=True, index=True)

    attempt_number = Column(Integer, default=1, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    score = Column(Float, default=0.0, nullable=False)

    # Independent problem-solving performance tracking
    was_assisted = Column(Boolean, default=False, nullable=False)  # True if hints/scaffolding were requested
    scaffolding_level_accessed = Column(Integer, default=0, nullable=False)  # 0: Independent, 1-4: Scaffolding tier accessed

    time_spent_seconds = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    student = relationship("Student", back_populates="attempts")
    activity = relationship("Activity", back_populates="attempts")
    assessment = relationship("Assessment", back_populates="attempts")
    code_submissions = relationship("CodeSubmission", back_populates="attempt", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="attempt")

    def __repr__(self):
        return f"<Attempt id={self.id} student={self.student_id} correct={self.is_correct} assisted={self.was_assisted}>"

