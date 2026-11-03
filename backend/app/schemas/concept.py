"""
Concept schemas adapter bridging Topic entities to client response format.
"""

from typing import Optional
from app.schemas.topic import TopicResponse, TopicBase


class ConceptResponse(TopicResponse):
    category: Optional[str] = None


class ConceptWithProblemCount(TopicResponse):
    category: Optional[str] = "General"
    problem_count: int = 0
    current_mastery_p: Optional[float] = 0.20
