"""
Topic database model.
Fine-grained pedagogical concept or computational skill.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Topic(Base):
    """
    Individual mathematical or algorithmic concept (e.g., 'Singly Linked List Reversal').
    Maintains separate skill tracking and prerequisite dependencies.
    """

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(60), unique=True, nullable=False, index=True)  # e.g., "IT22301-U1-SLL"
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(String(20), default="Intermediate", nullable=False)  # Beginner, Intermediate, Advanced
    order_index = Column(Integer, default=0, nullable=False)

    # Relationships
    unit = relationship("Unit", back_populates="topics")
    activities = relationship("Activity", back_populates="topic", cascade="all, delete-orphan")
    skill_states = relationship("LearnerSkillState", back_populates="topic", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="topic", cascade="all, delete-orphan")

    # Directed DAG relationships for prerequisites
    prerequisites = relationship(
        "Prerequisite",
        foreign_keys="[Prerequisite.topic_id]",
        back_populates="topic",
        cascade="all, delete-orphan",
    )
    required_by = relationship(
        "Prerequisite",
        foreign_keys="[Prerequisite.prerequisite_topic_id]",
        back_populates="prerequisite_topic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Topic id={self.id} code='{self.code}' name='{self.name}'>"
