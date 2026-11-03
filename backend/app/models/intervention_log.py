"""
Intervention log model for adaptive scaffolding and tutoring efficacy tracking.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class InterventionLog(Base):
    """
    Logs cognitive interventions triggered for a student (e.g. progressive scaffolding hint,
    misconception alert, code visualizer). Tracks whether the intervention facilitated independent success.
    """

    __tablename__ = "intervention_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)

    intervention_type = Column(String(50), nullable=False)  # SocraticHint, ConceptReminder, CodeSkeleton, TraceWalkthrough
    scaffolding_level = Column(Integer, default=1, nullable=False)  # Level 1 to 4
    trigger_reason = Column(String(100), nullable=False)  # RepeatedWrongAnswer, OffByOneDetected, CompilationFail
    diagnosis_summary = Column(Text, nullable=True)  # Cognitive diagnosis findings
    was_successful = Column(Boolean, nullable=True)  # Did the subsequent attempt pass independently?
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    learner = relationship("Learner", back_populates="interventions")
    problem = relationship("Problem", back_populates="interventions")

    def __repr__(self):
        return f"<InterventionLog id={self.id} learner={self.learner_id} type='{self.intervention_type}' level={self.scaffolding_level}>"
