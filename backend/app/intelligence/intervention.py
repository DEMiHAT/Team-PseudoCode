"""
Intervention Selection Engine.
Coordinates adaptive assistance decisions based on multidimensional cognitive evidence.
Architected with explicit feature extraction ready for Contextual Bandit and DKT integration.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.intelligence.scaffolding import ScaffoldingLevel
from app.intelligence.bkt import SkillType
from app.intelligence.misconceptions import MisconceptionRecord, MisconceptionStatus


class InterventionDecision(BaseModel):
    """Explainable cognitive intervention decision."""
    selected_level: ScaffoldingLevel
    intervention_type: str
    target_skill: str
    decision_rationale: str
    feature_vector: Dict[str, float] = Field(
        default_factory=dict,
        description="Normalized cognitive context features for Contextual Bandit / DKT policies"
    )
    suggested_action: str


class AdaptiveInterventionSelector:
    """
    Pedagogical decision policy engine.
    Considers:
      1. Current BKT mastery belief P(L_t)
      2. Confirmed vs Candidate misconceptions
      3. Number of attempts on current activity
      4. Previous scaffolding level delivered
      5. Historical independent success ratio
      6. Prior intervention outcomes (efficacy feedback)
    """

    @classmethod
    def select_intervention(
        cls,
        skill_mastery: Dict[str, float],
        misconception_history: Dict[str, MisconceptionRecord],
        activity_attempt_count: int,
        current_scaffolding_level: int,
        independent_success_ratio: float,
        last_intervention_successful: Optional[bool] = None,
        has_compilation_error: bool = False,
    ) -> InterventionDecision:
        """
        Determines the optimal scaffolding level and intervention strategy.
        Decision logic is 100% explainable and deterministic.
        """
        # Feature representation for Contextual Bandit (e.g. LinUCB state context)
        avg_mastery = sum(skill_mastery.values()) / len(skill_mastery) if skill_mastery else 0.20
        underflow_mastery = skill_mastery.get(SkillType.STACK_UNDERFLOW.value, 0.20)
        parentheses_mastery = skill_mastery.get(SkillType.PARENTHESES_VALIDATION.value, 0.20)

        confirmed_misconceptions = [
            m for m in misconception_history.values()
            if m.status == MisconceptionStatus.CONFIRMED
        ]

        feature_vector = {
            "avg_mastery": round(avg_mastery, 3),
            "underflow_mastery": round(underflow_mastery, 3),
            "parentheses_mastery": round(parentheses_mastery, 3),
            "attempt_count": float(activity_attempt_count),
            "scaffolding_level": float(current_scaffolding_level),
            "independent_ratio": round(independent_success_ratio, 3),
            "confirmed_misc_count": float(len(confirmed_misconceptions)),
        }

        # Rule 1: First Attempt -> Encourage Independent Problem-Solving (L0)
        if activity_attempt_count <= 1 and not has_compilation_error:
            return InterventionDecision(
                selected_level=ScaffoldingLevel.L0_INDEPENDENT,
                intervention_type="independent_challenge",
                target_skill=SkillType.STACK_CONCEPTUAL.value,
                decision_rationale="Initial attempt. Preserve pristine challenge to evaluate independent cognitive transfer.",
                feature_vector=feature_vector,
                suggested_action="Attempt the problem independently using your own algorithm design.",
            )

        # Rule 2: Compilation Block -> Syntax & Type Guidance (L1/L2)
        if has_compilation_error:
            return InterventionDecision(
                selected_level=ScaffoldingLevel.L2_TARGETED_HINT,
                intervention_type="syntax_remediation",
                target_skill=SkillType.STACK_JAVA_IMPL.value,
                decision_rationale="Compilation failure blocks logic evaluation. Deliver targeted hint on Java Stack imports and types.",
                feature_vector=feature_vector,
                suggested_action="Inspect generic wrapper types (e.g. Stack<Character>) and package imports.",
            )

        # Rule 3: Confirmed Misconception + Prior Intervention Failed -> Escalate to Algorithm Guide (L3) or Skeleton (L4)
        if confirmed_misconceptions:
            most_severe = confirmed_misconceptions[0]
            if last_intervention_successful is False and activity_attempt_count >= 3:
                # Persistent impasse despite prior hint -> Escalate to L4 Partial Implementation
                return InterventionDecision(
                    selected_level=ScaffoldingLevel.L4_PARTIAL_IMPL,
                    intervention_type="skeleton_remediation",
                    target_skill=SkillType.STACK_UNDERFLOW.value if "EMPTY" in most_severe.rule_code else SkillType.PARENTHESES_VALIDATION.value,
                    decision_rationale=(
                        f"Persistent confirmed misconception '{most_severe.name}' observed across multiple attempts "
                        f"and prior hint was unsuccessful. Escalating to L4 Partial Implementation skeleton."
                    ),
                    feature_vector=feature_vector,
                    suggested_action=most_severe.suggested_remedy,
                )
            else:
                # First or unescalated confirmed misconception -> Deliver Targeted L2 or L3
                target_level = ScaffoldingLevel.L3_ALGORITHM_GUIDE if activity_attempt_count >= 2 else ScaffoldingLevel.L2_TARGETED_HINT
                return InterventionDecision(
                    selected_level=target_level,
                    intervention_type="targeted_misconception_remediation",
                    target_skill=SkillType.PARENTHESES_VALIDATION.value,
                    decision_rationale=(
                        f"Confirmed cognitive bug '{most_severe.name}' detected with corroborating evidence. "
                        f"Serving {target_level.name} to guide invariant correction."
                    ),
                    feature_vector=feature_vector,
                    suggested_action=most_severe.suggested_remedy,
                )

        # Rule 4: High Mastery Learner (p_known >= 0.70) with Mistake -> Gentle Conceptual Prompt (L1)
        if avg_mastery >= 0.70:
            return InterventionDecision(
                selected_level=ScaffoldingLevel.L1_CONCEPTUAL_PROMPT,
                intervention_type="socratic_reflection",
                target_skill=SkillType.STACK_CONCEPTUAL.value,
                decision_rationale="High learner mastery belief. Deliver gentle L1 Socratic prompt to stimulate self-repair.",
                feature_vector=feature_vector,
                suggested_action="Reflect on the LIFO invariant and verify how your stack behaves on boundary cases.",
            )

        # Rule 5: Low Mastery Learner (< 0.40) with Repeated Impasse (>= 4 attempts) -> L5 Worked Solution
        if avg_mastery < 0.40 and activity_attempt_count >= 4 and last_intervention_successful is False:
            return InterventionDecision(
                selected_level=ScaffoldingLevel.L5_WORKED_SOLUTION,
                intervention_type="worked_example_demonstration",
                target_skill=SkillType.PARENTHESES_VALIDATION.value,
                decision_rationale="Severe cognitive impasse after 4+ failed attempts at low mastery. Present L5 Worked Solution.",
                feature_vector=feature_vector,
                suggested_action="Study the complete reference implementation and trace its state transitions.",
            )

        # Rule 6: Default Escalation by Attempt Count
        if activity_attempt_count == 2:
            return InterventionDecision(
                selected_level=ScaffoldingLevel.L2_TARGETED_HINT,
                intervention_type="boundary_hint",
                target_skill=SkillType.STACK_UNDERFLOW.value,
                decision_rationale="Second attempt failure. Deliver targeted hint on boundary conditions and empty stack guards.",
                feature_vector=feature_vector,
                suggested_action="Check whether a closing bracket might be evaluated when the stack has no elements.",
            )
        else:
            return InterventionDecision(
                selected_level=ScaffoldingLevel.L3_ALGORITHM_GUIDE,
                intervention_type="algorithmic_blueprint",
                target_skill=SkillType.PARENTHESES_VALIDATION.value,
                decision_rationale="Multiple attempt failure. Deliver step-by-step algorithmic pseudocode guidance.",
                feature_vector=feature_vector,
                suggested_action="Review the algorithmic loop invariants.",
            )


intervention_selector = AdaptiveInterventionSelector()

