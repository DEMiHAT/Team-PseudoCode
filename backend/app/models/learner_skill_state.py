"""
Learner Skill State database model.
Maintains fine-grained, concept-level cognitive mastery and independent performance evidence.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class LearnerSkillState(Base):
    """
    Maintains multidimensional mastery estimates per individual topic.
    Stores separate conceptual and practical learning evidence, tracks independent vs. assisted successes,
    and maintains Bayesian Knowledge Tracing (BKT) parameters. Avoids a single overall score.
    """

    __tablename__ = "learner_skill_states"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)

    # Bayesian Knowledge Tracing (BKT) Parameters
    p_known = Column(Float, default=0.20, nullable=False)  # Prior/Posterior P(L_t) in [0.0, 1.0]
    p_learn = Column(Float, default=0.15, nullable=False)  # P(T) transition probability
    p_guess = Column(Float, default=0.15, nullable=False)  # P(G) guess probability
    p_slip = Column(Float, default=0.10, nullable=False)   # P(S) slip probability

    # Separated Evidence Dimensions
    conceptual_mastery = Column(Float, default=0.0, nullable=False)  # Derived from conceptual quizzes & diagnostics [0.0, 1.0]
    practical_mastery = Column(Float, default=0.0, nullable=False)   # Derived from programming & test evaluation [0.0, 1.0]

    # Independent vs Assisted Performance Tracking
    independent_success_count = Column(Integer, default=0, nullable=False)  # Solved independently without interventions
    assisted_success_count = Column(Integer, default=0, nullable=False)     # Solved with scaffolding / hints
    consecutive_failures = Column(Integer, default=0, nullable=False)       # Current error streak
    total_attempts = Column(Integer, default=0, nullable=False)

    last_evaluated_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "topic_id", name="uq_student_topic_skill_state"),
    )

    # Relationships
    student = relationship("Student", back_populates="skill_states")
    topic = relationship("Topic", back_populates="skill_states")

    def __repr__(self):
        return (
            f"<LearnerSkillState student_id={self.student_id} topic_id={self.topic_id} "
            f"p_known={self.p_known:.2f} conceptual={self.conceptual_mastery:.2f} practical={self.practical_mastery:.2f}>"
        )

