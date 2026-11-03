"""
Context Retrieval Interface for AI DSA Tutoring.
Aggregates curricular location, learner cognitive state, code, and execution evidence.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.topic import Topic
from app.models.unit import Unit
from app.models.subject import Subject
from app.ai_tutor.schemas import TutorContext, CodeExecutionEvidence
from app.ai_tutor.learner_state_bridge import learner_state_bridge, LearnerStateBridge
from app.core.logging import logger


class ContextRetriever:
    """
    Assembles a coherent TutorContext for the AI Tutor from DB entities,
    cognitive models, and incoming runtime parameters.
    """

    def __init__(self, state_bridge: Optional[LearnerStateBridge] = None):
        self.state_bridge = state_bridge or learner_state_bridge

    def build_context(
        self,
        student_id: int,
        db: Optional[Session] = None,
        topic_id: Optional[int] = None,
        activity_id: Optional[int] = None,
        scaffold_level: Optional[int] = None,
        current_code: str = "",
        execution_evidence: Optional[CodeExecutionEvidence] = None,
    ) -> TutorContext:
        """
        Retrieves all necessary context variables for intelligent tutoring.
        """
        subject_name = "IT22301 – Data Structures and Algorithms"
        unit_name = "Unit 2: Linear Data Structures"
        topic_name = "Stacks"
        subtopic_name = "Array Implementation & Boundary Invariants"

        # Resolve curricular hierarchy from database if available
        if db is not None:
            try:
                if activity_id:
                    activity = db.query(Activity).filter(Activity.id == activity_id).first()
                    if activity and activity.topic:
                        topic_id = activity.topic_id
                        subtopic_name = activity.title

                if topic_id:
                    topic = db.query(Topic).filter(Topic.id == topic_id).first()
                    if topic:
                        topic_name = topic.name
                        if topic.unit:
                            unit_name = topic.unit.name
                            if topic.unit.subject:
                                subject_name = f"{topic.unit.subject.code} – {topic.unit.subject.name}"
            except Exception as exc:
                logger.warning(f"ContextRetriever metadata lookup failed: {exc}")

        # Fetch learner cognitive profile
        profile = self.state_bridge.get_learner_cognitive_profile(
            db=db,
            student_id=student_id,
            topic_id=topic_id,
        )

        effective_scaffold = scaffold_level if scaffold_level is not None else 1
        evidence = execution_evidence or CodeExecutionEvidence(has_evidence=False)

        return TutorContext(
            student_id=student_id,
            subject=subject_name,
            unit=unit_name,
            topic=topic_name,
            subtopic=subtopic_name,
            estimated_mastery=profile["estimated_mastery"],
            mastery_level_label=profile["mastery_level_label"],
            previous_errors=profile["recent_errors"],
            previous_assistance=profile["recent_interventions"],
            scaffold_level=effective_scaffold,
            current_code=current_code,
            execution_evidence=evidence,
            confirmed_misconceptions=profile["confirmed_misconceptions"],
            candidate_misconceptions=profile["candidate_misconceptions"],
        )


# Singleton instance
context_retriever = ContextRetriever()
