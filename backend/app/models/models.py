"""
SQLAlchemy database models for the Adaptive AI Learning Platform.
Designed for Class 8 Mathematics personalized learning.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    """Return current UTC timestamp with timezone."""
    return datetime.now(timezone.utc)


class Learner(Base):
    """
    Represents an individual student.
    """
    __tablename__ = "learners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    display_name = Column(String(100), nullable=False)

    # Relationships
    attempts = relationship("Attempt", back_populates="learner", cascade="all, delete-orphan")
    masteries = relationship("Mastery", back_populates="learner", cascade="all, delete-orphan")
    interventions = relationship("InterventionHistory", back_populates="learner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Learner id={self.id} display_name='{self.display_name}'>"


class Concept(Base):
    """
    Represents a mathematical concept or curriculum topic (e.g., 'Linear Equations in One Variable').
    """
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    questions = relationship("Question", back_populates="concept", cascade="all, delete-orphan")
    masteries = relationship("Mastery", back_populates="concept", cascade="all, delete-orphan")
    interventions = relationship("InterventionHistory", back_populates="concept", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Concept id={self.id} name='{self.name}'>"


class Question(Base):
    """
    Represents a practice question or diagnostic item associated with a mathematical concept.
    Includes misconception rules to diagnose typical Class 8 algebraic and arithmetic bugs.
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    correct_answer = Column(String(255), nullable=False)
    misconception_rule = Column(Text, nullable=True)  # JSON or rule string (e.g. "if answer == -4, sign error on transposition")

    # Relationships
    concept = relationship("Concept", back_populates="questions")
    attempts = relationship("Attempt", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question id={self.id} concept_id={self.concept_id}>"


class Attempt(Base):
    """
    Records a student's answer to a question for tracking and BKT estimation.
    """
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    answer = Column(String(255), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    learner = relationship("Learner", back_populates="attempts")
    question = relationship("Question", back_populates="attempts")

    def __repr__(self):
        return f"<Attempt id={self.id} learner={self.learner_id} correct={self.is_correct}>"


class Mastery(Base):
    """
    Tracks the estimated Bayesian Knowledge Tracing (BKT) probability p(L) that
    a learner understands a particular concept.
    """
    __tablename__ = "mastery"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    mastery_probability = Column(Float, default=0.1, nullable=False)  # Prior / posterior probability between 0.0 and 1.0

    # Relationships
    learner = relationship("Learner", back_populates="masteries")
    concept = relationship("Concept", back_populates="masteries")

    def __repr__(self):
        return f"<Mastery id={self.id} learner={self.learner_id} concept={self.concept_id} p={self.mastery_probability}>"


class InterventionHistory(Base):
    """
    Logs teaching interventions (scaffolding, hints, worked examples),
    evaluates whether the student succeeded independently, and tracks pedagogical efficacy.
    """
    __tablename__ = "intervention_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    intervention_type = Column(String(100), nullable=False)  # e.g., 'socratic_hint', 'visual_analogy', 'worked_example'
    diagnosis = Column(Text, nullable=True)  # Identified misconception
    pre_score = Column(Float, nullable=True)
    post_score = Column(Float, nullable=True)
    independent_success = Column(Boolean, nullable=True)  # Did student solve a subsequent transfer question without hints?
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    learner = relationship("Learner", back_populates="interventions")
    concept = relationship("Concept", back_populates="interventions")

    def __repr__(self):
        return f"<InterventionHistory id={self.id} learner={self.learner_id} type='{self.intervention_type}'>"

