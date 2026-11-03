"""
Learner database model representing an undergraduate engineering student.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Learner(Base):
    """Undergraduate student enrolled in IT22301."""

    __tablename__ = "learners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "22IT045"
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    semester = Column(Integer, default=3, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    submissions = relationship("Submission", back_populates="learner", cascade="all, delete-orphan")
    knowledge_states = relationship("KnowledgeState", back_populates="learner", cascade="all, delete-orphan")
    interventions = relationship("InterventionLog", back_populates="learner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Learner id={self.id} student_id='{self.student_id}' name='{self.full_name}'>"
