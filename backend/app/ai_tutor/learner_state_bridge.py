"""
Learner-State Integration Bridge.
Connects database skill tracking, Bayesian Knowledge Tracing (BKT),
and misconception diagnosis to the AI Tutoring context.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.learner_skill_state import LearnerSkillState
from app.models.intervention import Intervention
from app.models.attempt import Attempt
from app.intelligence.bkt import SkillType, BayesianKnowledgeTracer
from app.intelligence.misconceptions import CognitiveMisconceptionDiagnoser, get_default_diagnoser
from app.core.logging import logger


class LearnerStateBridge:
    """
    Translates raw database metrics and cognitive tracing algorithms
    into high-fidelity pedagogical indicators for AI tutoring.
    """

    def __init__(self, diagnoser: Optional[CognitiveMisconceptionDiagnoser] = None):
        self.diagnoser = diagnoser or get_default_diagnoser()
        self.bkt_tracer = BayesianKnowledgeTracer()

    def get_learner_cognitive_profile(
        self,
        db: Optional[Session],
        student_id: int,
        topic_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Gathers multi-skill mastery probabilities, cognitive proficiency label,
        and recent pedagogical intervention logs.
        """
        mastery_map: Dict[str, float] = {}
        recent_interventions: List[str] = []
        recent_errors: List[str] = []

        if db is not None:
            try:
                # Query topic skill state if available
                query = db.query(LearnerSkillState).filter(LearnerSkillState.student_id == student_id)
                if topic_id:
                    query = query.filter(LearnerSkillState.topic_id == topic_id)
                states = query.all()

                for state in states:
                    topic_name = state.topic.name if state.topic else f"topic_{state.topic_id}"
                    mastery_map[topic_name] = round(state.p_known, 3)

                # Query recent interventions
                interventions = (
                    db.query(Intervention)
                    .filter(Intervention.student_id == student_id)
                    .order_by(Intervention.created_at.desc())
                    .limit(3)
                    .all()
                )
                for inv in interventions:
                    recent_interventions.append(
                        f"Tier {inv.scaffolding_tier} ({inv.intervention_type}): {inv.trigger_reason}"
                    )

                # Query recent attempts for error logs
                attempts = (
                    db.query(Attempt)
                    .filter(Attempt.student_id == student_id)
                    .order_by(Attempt.started_at.desc())
                    .limit(3)
                    .all()
                )
                for att in attempts:
                    if not att.is_correct:
                        recent_errors.append(f"Failed attempt #{att.attempt_number} (score: {att.score})")

            except Exception as exc:
                logger.warning(f"LearnerStateBridge DB query failed: {exc}")

        # Fallback / baseline defaults if no DB records exist yet
        if not mastery_map:
            mastery_map = {
                SkillType.STACK_CONCEPTUAL.value: 0.35,
                SkillType.STACK_JAVA_IMPL.value: 0.25,
                SkillType.STACK_UNDERFLOW.value: 0.20,
                SkillType.PARENTHESES_VALIDATION.value: 0.20,
            }

        avg_mastery = sum(mastery_map.values()) / max(len(mastery_map), 1)
        proficiency_label = self._calculate_proficiency_label(avg_mastery)

        confirmed_misconceptions = [
            m.name for m in self.diagnoser.get_confirmed_misconceptions()
        ]
        candidate_misconceptions = [
            m.name for m in self.diagnoser.get_candidate_misconceptions()
        ]

        return {
            "estimated_mastery": mastery_map,
            "average_mastery": round(avg_mastery, 3),
            "mastery_level_label": proficiency_label,
            "recent_interventions": recent_interventions,
            "recent_errors": recent_errors,
            "confirmed_misconceptions": confirmed_misconceptions,
            "candidate_misconceptions": candidate_misconceptions,
        }

    @staticmethod
    def _calculate_proficiency_label(mastery: float) -> str:
        """Categorizes raw probability into a pedagogical descriptor."""
        if mastery >= 0.85:
            return "Mastered"
        if mastery >= 0.65:
            return "Competent"
        if mastery >= 0.40:
            return "Developing"
        return "Novice"


# Singleton instance
learner_state_bridge = LearnerStateBridge()
