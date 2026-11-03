"""
Activity database model.
Represents a learning exercise, coding task, or conceptual assessment item.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Activity(Base):
    """
    Practice problem, conceptual task, or code implementation exercise.
    Associated with a specific curriculum topic.
    """

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # 'coding_exercise', 'conceptual_quiz', 'trace_walkthrough'
    description_md = Column(Text, nullable=False)
    difficulty = Column(String(20), default="Medium", nullable=False)  # Easy, Medium, Hard
    starter_template = Column(Text, nullable=True)  # Java starter code or initial template
    solution_reference = Column(Text, nullable=True)
    test_cases_json = Column(Text, nullable=True)  # JSON encoded test suite
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="activities")
    attempts = relationship("Attempt", back_populates="activity", cascade="all, delete-orphan")
    code_submissions = relationship("CodeSubmission", back_populates="activity", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="activity", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Activity id={self.id} slug='{self.slug}' type='{self.activity_type}'>"
