"""
Student database model.
Represents an enrolled student in the intelligent tutoring system.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class Student(Base):
    """
    Core student entity. Supports multiple students across multiple courses/subjects.
    """

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    external_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "22IT045"
    full_name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # 1-to-1 relationship with learner preferences
    preference = relationship("Preference", back_populates="student", uselist=False, cascade="all, delete-orphan")

    # 1-to-many relationships
    skill_states = relationship("LearnerSkillState", back_populates="student", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="student", cascade="all, delete-orphan")
    code_submissions = relationship("CodeSubmission", back_populates="student", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="student", cascade="all, delete-orphan")
    interaction_events = relationship("InteractionEvent", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student id={self.id} external_id='{self.external_id}' name='{self.full_name}'>"
