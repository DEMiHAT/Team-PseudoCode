"""
CRUD package exporting data access repositories for all entities.
"""

from app.crud.crud_student import student, preference
from app.crud.crud_curriculum import subject, unit, topic, prerequisite
from app.crud.crud_skill_state import learner_skill_state
from app.crud.crud_activity import activity, assessment
from app.crud.crud_attempt import attempt, code_submission, execution_result
from app.crud.crud_intervention import intervention
from app.crud.crud_interaction_event import interaction_event

__all__ = [
    "student",
    "preference",
    "subject",
    "unit",
    "topic",
    "prerequisite",
    "learner_skill_state",
    "activity",
    "assessment",
    "attempt",
    "code_submission",
    "execution_result",
    "intervention",
    "interaction_event",
]

