"""
Learner State Management Module.
Maintains multi-dimensional skill vectors, misconception lifecycle, and independent success records.
CRITICAL INVARIANT: Mastery scores are strictly calculated via BKT mathematics from assessment/execution evidence.
LLMs are NEVER permitted to assign or modify mastery scores.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.intelligence.bkt import SkillType, BayesianKnowledgeTracer, bkt_engine, BKTUpdateResult
from app.intelligence.error_classifier import ClassifiedError, error_classifier
from app.intelligence.misconceptions import (
    MisconceptionRecord,
    CognitiveMisconceptionDiagnoser,
    misconception_diagnoser,
    MisconceptionStatus,
)
from app.intelligence.scaffolding import ScaffoldingLevel
from app.intelligence.intervention import AdaptiveInterventionSelector, InterventionDecision, intervention_selector


class SkillStateSnapshot(BaseModel):
    """Snapshot of a single fine-grained skill state."""
    skill_name: str
    p_known: float
    mastery_percentage: float
    is_mastered: bool
    total_attempts: int
    independent_successes: int
    assisted_successes: int


class LearnerCognitiveState(BaseModel):
    """Complete multi-dimensional cognitive state of a student."""
    student_id: int
    skills: Dict[str, SkillStateSnapshot]
    active_misconceptions: Dict[str, MisconceptionRecord]
    current_activity_id: Optional[int] = None
    activity_attempt_count: int = 0
    current_scaffolding_level: int = 0
    last_intervention_successful: Optional[bool] = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearnerStateManager:
    """
    Manages the lifecycle of a learner's cognitive state.
    Coordinates between BKT, error classifier, misconception accumulator, and intervention selector.
    """

    def __init__(self, tracer: Optional[BayesianKnowledgeTracer] = None):
        self.tracer = tracer or bkt_engine

    def initialize_state(self, student_id: int) -> LearnerCognitiveState:
        """Initializes a new learner cognitive state with calibrated default priors."""
        skills: Dict[str, SkillStateSnapshot] = {}
        for skill in SkillType:
            params = self.tracer.get_skill_params(skill)
            skills[skill.value] = SkillStateSnapshot(
                skill_name=skill.value,
                p_known=params.p_init,
                mastery_percentage=round(params.p_init * 100.0, 1),
                is_mastered=params.p_init >= params.mastery_threshold,
                total_attempts=0,
                independent_successes=0,
                assisted_successes=0,
            )

        return LearnerCognitiveState(
            student_id=student_id,
            skills=skills,
            active_misconceptions={},
            activity_attempt_count=0,
            current_scaffolding_level=0,
        )

    def process_submission_evidence(
        self,
        state: LearnerCognitiveState,
        activity_id: int,
        code: str,
        is_passed: bool,
        was_assisted: bool,
        compile_output: Optional[str] = None,
        stderr: Optional[str] = None,
        test_failures: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Processes physical execution evidence to update BKT skills, candidate/confirmed misconceptions,
        and determines the next recommended intervention.
        """
        # Reset attempt counter if moving to a new activity
        if state.current_activity_id != activity_id:
            state.current_activity_id = activity_id
            state.activity_attempt_count = 0
            state.current_scaffolding_level = 0
            state.last_intervention_successful = None

        state.activity_attempt_count += 1
        has_compilation = bool(compile_output and compile_output.strip())

        # 1. Error Classification
        classified_errors = error_classifier.classify_execution(
            code=code,
            compile_output=compile_output,
            stderr=stderr,
            test_failures=test_failures,
        )

        # 2. Misconception Evidence Accumulation
        # INVARIANT: Single errors remain candidates; only repeated errors confirm
        if not is_passed:
            state.active_misconceptions = misconception_diagnoser.evaluate_errors(
                classified_errors=classified_errors,
                existing_history=state.active_misconceptions,
            )
        else:
            # Demonstration of clean success resolves active bugs
            state.active_misconceptions = misconception_diagnoser.mark_resolved_misconceptions(
                state.active_misconceptions,
                successful_run=is_passed and not was_assisted,
            )

        # 3. Objective Evidence Mapping to Discrete Skills
        # Determine performance on individual skills from error signatures
        evidence_map: Dict[SkillType, bool] = {
            SkillType.STACK_JAVA_IMPL: not has_compilation,
            SkillType.STACK_UNDERFLOW: not any("EmptyStack" in e.title or "Underflow" in e.title for e in classified_errors),
            SkillType.PARENTHESES_VALIDATION: not any("Nested" in e.title or "Matching" in e.title or "Invariant" in e.title for e in classified_errors),
            SkillType.STACK_CONCEPTUAL: is_passed or (not has_compilation and len(classified_errors) <= 1),
        }

        # 4. Bayesian Knowledge Tracing Updates
        bkt_results: Dict[str, BKTUpdateResult] = {}
        for skill_enum, skill_passed in evidence_map.items():
            current_snap = state.skills[skill_enum.value]
            bkt_res = self.tracer.update_skill(
                skill=skill_enum,
                current_p_known=current_snap.p_known,
                is_correct=skill_passed,
            )
            bkt_results[skill_enum.value] = bkt_res

            # Update snapshot metrics
            current_snap.p_known = bkt_res.next_prior_p_known
            current_snap.mastery_percentage = bkt_res.mastery_percentage
            current_snap.is_mastered = bkt_res.is_mastered
            current_snap.total_attempts += 1
            if skill_passed:
                if was_assisted:
                    current_snap.assisted_successes += 1
                else:
                    current_snap.independent_successes += 1

        # 5. Calculate Independent Success Ratio
        total_successes = sum(s.independent_successes + s.assisted_successes for s in state.skills.values())
        independent_successes = sum(s.independent_successes for s in state.skills.values())
        independent_ratio = (independent_successes / total_successes) if total_successes > 0 else 0.5

        # 6. Adaptive Intervention Selection
        skill_masteries = {s_name: s_snap.p_known for s_name, s_snap in state.skills.items()}
        intervention_decision: Optional[InterventionDecision] = None

        if not is_passed:
            intervention_decision = intervention_selector.select_intervention(
                skill_mastery=skill_masteries,
                misconception_history=state.active_misconceptions,
                activity_attempt_count=state.activity_attempt_count,
                current_scaffolding_level=state.current_scaffolding_level,
                independent_success_ratio=independent_ratio,
                last_intervention_successful=state.last_intervention_successful,
                has_compilation_error=has_compilation,
            )
            state.current_scaffolding_level = intervention_decision.selected_level.value

        state.last_updated = datetime.now(timezone.utc)

        return {
            "is_passed": is_passed,
            "was_assisted": was_assisted,
            "classified_errors": [e.model_dump() for e in classified_errors],
            "active_misconceptions": {k: v.model_dump() for k, v in state.active_misconceptions.items()},
            "bkt_updates": {k: v.model_dump() for k, v in bkt_results.items()},
            "recommended_intervention": intervention_decision.model_dump() if intervention_decision else None,
            "state_snapshot": state.model_dump(),
        }


learner_state_manager = LearnerStateManager()
