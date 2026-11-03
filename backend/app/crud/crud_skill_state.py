"""
CRUD operations for LearnerSkillState.
Manages concept-level Bayesian Knowledge Tracing updates and independent vs assisted metrics.
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.learner_skill_state import LearnerSkillState
from app.schemas.skill_state import SkillStateCreate, SkillStateUpdate
from app.intelligence.bkt_engine import BKTEngine


class CRUDLearnerSkillState(CRUDBase[LearnerSkillState, SkillStateCreate, SkillStateUpdate]):
    def get_by_student_and_topic(
        self, db: Session, *, student_id: int, topic_id: int
    ) -> Optional[LearnerSkillState]:
        return (
            db.query(LearnerSkillState)
            .filter(
                LearnerSkillState.student_id == student_id,
                LearnerSkillState.topic_id == topic_id,
            )
            .first()
        )

    def get_all_for_student(
        self, db: Session, *, student_id: int
    ) -> List[LearnerSkillState]:
        """Returns fine-grained individual concept mastery records without collapsing into a single score."""
        return (
            db.query(LearnerSkillState)
            .filter(LearnerSkillState.student_id == student_id)
            .all()
        )

    def get_or_create(
        self, db: Session, *, student_id: int, topic_id: int
    ) -> LearnerSkillState:
        state = self.get_by_student_and_topic(db, student_id=student_id, topic_id=topic_id)
        if not state:
            state = LearnerSkillState(
                student_id=student_id,
                topic_id=topic_id,
                p_known=0.20,
                p_learn=0.15,
                p_guess=0.15,
                p_slip=0.10,
                conceptual_mastery=0.0,
                practical_mastery=0.0,
                independent_success_count=0,
                assisted_success_count=0,
                consecutive_failures=0,
                total_attempts=0,
            )
            db.add(state)
            db.commit()
            db.refresh(state)
        return state

    def record_attempt_outcome(
        self,
        db: Session,
        *,
        student_id: int,
        topic_id: int,
        is_correct: bool,
        was_assisted: bool,
        evidence_type: str = "practical",  # "conceptual" or "practical"
    ) -> LearnerSkillState:
        """
        Updates knowledge parameters, separating conceptual vs practical mastery,
        and accurately tracking independent vs assisted problem-solving.
        """
        state = self.get_or_create(db, student_id=student_id, topic_id=topic_id)

        # 1. Update Bayesian Knowledge Tracing belief
        bkt_res = BKTEngine.update_knowledge_state(
            prior_p_known=state.p_known,
            is_correct=is_correct,
            p_transit=state.p_learn,
            p_guess=state.p_guess,
            p_slip=state.p_slip,
        )
        state.p_known = bkt_res["next_prior_p_known"]

        # 2. Update separated learning evidence
        if evidence_type == "conceptual":
            delta = 0.15 if is_correct else -0.10
            state.conceptual_mastery = max(0.0, min(1.0, state.conceptual_mastery + delta))
        else:
            delta = 0.20 if is_correct else -0.10
            state.practical_mastery = max(0.0, min(1.0, state.practical_mastery + delta))

        # 3. Track independent problem-solving vs assisted success
        state.total_attempts += 1
        if is_correct:
            state.consecutive_failures = 0
            if was_assisted:
                state.assisted_success_count += 1
            else:
                state.independent_success_count += 1
        else:
            state.consecutive_failures += 1

        state.last_evaluated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(state)
        return state


learner_skill_state = CRUDLearnerSkillState(LearnerSkillState)
