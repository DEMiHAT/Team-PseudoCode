"""
Knowledge state model storing Bayesian Knowledge Tracing (BKT) parameters per concept.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class KnowledgeState(Base):
    """
    Maintains the estimated cognitive mastery state p(L) for a learner on a given concept.
    Includes the four standard BKT model parameters:
    - p_known: P(L_t) - Probability that the student has mastered the concept
    - p_learn: P(T)   - Probability of transitioning from unmastered to mastered
    - p_guess: P(G)   - Probability of guessing correctly without mastery
    - p_slip:  P(S)   - Probability of making an error despite mastery
    """

    __tablename__ = "knowledge_states"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)

    p_known = Column(Float, default=0.2, nullable=False)
    p_learn = Column(Float, default=0.15, nullable=False)
    p_guess = Column(Float, default=0.15, nullable=False)
    p_slip = Column(Float, default=0.10, nullable=False)

    total_attempts = Column(Integer, default=0, nullable=False)
    successful_attempts = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    learner = relationship("Learner", back_populates="knowledge_states")
    concept = relationship("Concept", back_populates="knowledge_states")

    def __repr__(self):
        return f"<KnowledgeState learner={self.learner_id} concept={self.concept_id} p_known={self.p_known:.2f}>"
