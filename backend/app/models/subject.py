"""
Subject database model.
Supports multi-course and multi-subject curricula.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Subject(Base):
    """
    Curriculum Subject or Course (e.g., IT22301 - Data Structures and Algorithms).
    """

    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "IT22301"
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    units = relationship("Unit", back_populates="subject", cascade="all, delete-orphan", order_by="Unit.unit_number")
    assessments = relationship("Assessment", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject id={self.id} code='{self.code}' name='{self.name}'>"
