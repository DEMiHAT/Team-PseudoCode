"""
Problem database model for Java coding exercises in IT22301.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Problem(Base):
    """
    DSA coding problem associated with a specific curriculum concept.
    Includes Java starter templates, drivers, and structured test cases.
    """

    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    difficulty = Column(String(20), default="Easy", nullable=False)  # Easy, Medium, Hard
    description_md = Column(Text, nullable=False)
    starter_code_java = Column(Text, nullable=False)
    driver_code_java = Column(Text, nullable=True)  # Java wrapper harness for Judge0 test execution
    test_cases_json = Column(Text, nullable=False)  # JSON-encoded array of test cases: [{input, expected, hidden}]
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    concept = relationship("Concept", back_populates="problems")
    submissions = relationship("Submission", back_populates="problem", cascade="all, delete-orphan")
    interventions = relationship("InterventionLog", back_populates="problem", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Problem id={self.id} slug='{self.slug}' difficulty='{self.difficulty}'>"
