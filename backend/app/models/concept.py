"""
Concept / Topic database model for IT22301 syllabus topics.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Concept(Base):
    """
    Curriculum unit concept (e.g. 'Binary Search Trees', 'Stack Evaluation', 'Circular Queues').
    """

    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "IT22301-MOD2-STACK"
    name = Column(String(120), nullable=False)
    category = Column(String(80), nullable=False, index=True)  # e.g., "Linear Data Structures"
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)

    # Relationships
    problems = relationship("Problem", back_populates="concept", cascade="all, delete-orphan")
    knowledge_states = relationship("KnowledgeState", back_populates="concept", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Concept id={self.id} code='{self.code}' name='{self.name}'>"
