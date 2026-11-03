"""
Prerequisite database model.
Models directed dependencies between curriculum topics.
"""

from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Prerequisite(Base):
    """
    Directed dependency edge in the knowledge DAG.
    Specifies that mastering `prerequisite_topic_id` is required before `topic_id`.
    """

    __tablename__ = "prerequisites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    prerequisite_topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    strength = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0 dependency weighting
    is_mandatory = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("topic_id", "prerequisite_topic_id", name="uq_topic_prerequisite"),
    )

    # Relationships
    topic = relationship("Topic", foreign_keys=[topic_id], back_populates="prerequisites")
    prerequisite_topic = relationship("Topic", foreign_keys=[prerequisite_topic_id], back_populates="required_by")

    def __repr__(self):
        return f"<Prerequisite topic_id={self.topic_id} requires={self.prerequisite_topic_id} mandatory={self.is_mandatory}>"
