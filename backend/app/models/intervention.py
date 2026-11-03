"""
Intervention database model.
Tracks assistance history, cognitive scaffolds, and pedagogical efficacy.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Intervention(Base):
    """
    Pedagogical intervention or assistance event delivered to a learner.
    Logs scaffolding tier, trigger condition, and whether subsequent attempts succeeded.
    """

    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="SET NULL"), nullable=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id", ondelete="SET NULL"), nullable=True, index=True)

    intervention_type = Column(String(60), nullable=False)  # 'socratic_hint', 'pseudocode_scaffold', 'state_trace_visualizer', 'code_skeleton'
    scaffolding_tier = Column(Integer, default=1, nullable=False)  # Level 1 to 4
    trigger_reason = Column(String(100), nullable=False)  # 'off_by_one_detected', 'consecutive_failures_3', 'student_requested'
    hint_content = Column(Text, nullable=False)
    is_llm_generated = Column(Boolean, default=False, nullable=False)
    subsequent_attempt_successful = Column(Boolean, nullable=True)  # Pedagogical efficacy feedback loop

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="interventions")
    topic = relationship("Topic", back_populates="interventions")
    activity = relationship("Activity", back_populates="interventions")
    attempt = relationship("Attempt", back_populates="interventions")

    def __repr__(self):
        return f"<Intervention id={self.id} student={self.student_id} tier={self.scaffolding_tier} type='{self.intervention_type}'>"
