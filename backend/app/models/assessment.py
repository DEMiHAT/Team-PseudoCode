"""
Assessment database model.
Diagnostic tests, milestone exams, or independent transfer evaluations.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Assessment(Base):
    """
    Formal or formative assessment container across topics or units.
    """

    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # 'diagnostic_pretest', 'unit_formative', 'transfer_posttest'
    total_points = Column(Float, default=100.0, nullable=False)
    time_limit_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="assessments")
    attempts = relationship("Attempt", back_populates="assessment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assessment id={self.id} title='{self.title}' type='{self.assessment_type}'>"
