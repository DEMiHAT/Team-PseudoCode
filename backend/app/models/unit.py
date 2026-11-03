"""
Unit database model.
Represents a syllabus module/unit belonging to a subject.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Unit(Base):
    """
    Syllabus Unit (e.g. Unit 1: Linear Collections, Unit 2: Stacks and Queues).
    """

    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_number = Column(Integer, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("subject_id", "unit_number", name="uq_subject_unit_number"),
    )

    # Relationships
    subject = relationship("Subject", back_populates="units")
    topics = relationship("Topic", back_populates="unit", cascade="all, delete-orphan", order_by="Topic.order_index")

    def __repr__(self):
        return f"<Unit id={self.id} subject_id={self.subject_id} unit_number={self.unit_number} title='{self.title}'>"
