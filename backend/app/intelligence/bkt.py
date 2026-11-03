"""
Bayesian Knowledge Tracing (BKT) Module.
Implements the standard Corbett & Anderson (1995) cognitive modeling equations.
Maintains separate, independent learning skill states for fine-grained concept tracking.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class SkillType(str, Enum):
    """Specific learning skills tracked independently in the tutoring system."""
    STACK_CONCEPTUAL = "stack_conceptual"           # LIFO mechanics, push/pop semantics
    STACK_JAVA_IMPL = "stack_java_impl"             # Syntax, imports, generic types (Stack<Character>)
    STACK_UNDERFLOW = "stack_underflow"             # Calling pop/peek without isEmpty() guard
    PARENTHESES_VALIDATION = "parentheses_validation" # Bracket correspondence, balance invariants


class SkillParameters(BaseModel):
    """Calibrated BKT parameters for a distinct skill."""
    p_init: float = Field(default=0.20, ge=0.0, le=1.0, description="P(L_0) Initial prior mastery belief")
    p_transit: float = Field(default=0.15, ge=0.0, le=1.0, description="P(T) Learning transition probability")
    p_guess: float = Field(default=0.15, ge=0.0, le=1.0, description="P(G) Probability of guessing correctly without mastery")
    p_slip: float = Field(default=0.10, ge=0.0, le=1.0, description="P(S) Probability of error despite mastery")
    mastery_threshold: float = Field(default=0.85, ge=0.5, le=1.0, description="Mastery threshold")


# Calibrated defaults for each required skill domain
DEFAULT_SKILL_PARAMETERS: Dict[SkillType, SkillParameters] = {
    SkillType.STACK_CONCEPTUAL: SkillParameters(
        p_init=0.25,
        p_transit=0.18,
        p_guess=0.20,
        p_slip=0.08,
        mastery_threshold=0.85,
    ),
    SkillType.STACK_JAVA_IMPL: SkillParameters(
        p_init=0.20,
        p_transit=0.15,
        p_guess=0.15,
        p_slip=0.12,
        mastery_threshold=0.85,
    ),
    SkillType.STACK_UNDERFLOW: SkillParameters(
        p_init=0.15,
        p_transit=0.20,
        p_guess=0.10,
        p_slip=0.10,
        mastery_threshold=0.85,
    ),
    SkillType.PARENTHESES_VALIDATION: SkillParameters(
        p_init=0.20,
        p_transit=0.14,
        p_guess=0.12,
        p_slip=0.10,
        mastery_threshold=0.85,
    ),
}


class BKTUpdateResult(BaseModel):
    """Result of a Bayesian Knowledge Tracing posterior update."""
    skill_name: str
    is_correct: bool
    prior_p_known: float
    posterior_p_known: float
    next_prior_p_known: float
    mastery_percentage: float
    is_mastered: bool
    evidence_weight: float


class BayesianKnowledgeTracer:
    """
    Pure cognitive Bayesian Knowledge Tracing engine.
    Completely decoupled from LLMs: all calculations are strictly based on
    objective assessment and sandboxed execution evidence.
    """

    def __init__(self, skill_parameters: Optional[Dict[SkillType, SkillParameters]] = None):
        self.skill_params = skill_parameters or DEFAULT_SKILL_PARAMETERS

    def get_skill_params(self, skill: SkillType) -> SkillParameters:
        """Retrieves parameters for a given skill or returns safe defaults."""
        return self.skill_params.get(skill, SkillParameters())

    def update_skill(
        self,
        skill: SkillType,
        current_p_known: float,
        is_correct: bool,
        custom_params: Optional[SkillParameters] = None,
    ) -> BKTUpdateResult:
        """
        Executes a single BKT observation update step.

        Formulas:
          Posterior:
            If Correct:   P(L_t | Correct) = (P(L_t) * (1 - P(S))) / [P(L_t) * (1 - P(S)) + (1 - P(L_t)) * P(G)]
            If Incorrect: P(L_t | Incorrect) = (P(L_t) * P(S)) / [P(L_t) * P(S) + (1 - P(L_t)) * (1 - P(G))]

          Transition to Next State:
            P(L_{t+1}) = P(L_t | obs) + (1 - P(L_t | obs)) * P(T)
        """
        params = custom_params or self.get_skill_params(skill)

        # Numerical stability clamp to avoid degenerate zero/one probabilities
        p_l = max(0.001, min(0.999, float(current_p_known)))

        # 1. Calculate observation likelihood and posterior
        if is_correct:
            numerator = p_l * (1.0 - params.p_slip)
            denominator = (p_l * (1.0 - params.p_slip)) + ((1.0 - p_l) * params.p_guess)
        else:
            numerator = p_l * params.p_slip
            denominator = (p_l * params.p_slip) + ((1.0 - p_l) * (1.0 - params.p_guess))

        posterior = numerator / denominator if denominator > 0 else p_l
        posterior = max(0.001, min(0.999, posterior))

        # 2. Skill learning transition towards next opportunity
        next_prior = posterior + ((1.0 - posterior) * params.p_transit)
        next_prior = max(0.0, min(1.0, next_prior))

        is_mastered = next_prior >= params.mastery_threshold

        return BKTUpdateResult(
            skill_name=skill.value,
            is_correct=is_correct,
            prior_p_known=round(p_l, 4),
            posterior_p_known=round(posterior, 4),
            next_prior_p_known=round(next_prior, 4),
            mastery_percentage=round(next_prior * 100.0, 1),
            is_mastered=is_mastered,
            evidence_weight=round(abs(next_prior - p_l), 4),
        )

    def update_multi_skill(
        self,
        current_skills: Dict[SkillType, float],
        evidence: Dict[SkillType, bool],
    ) -> Dict[str, BKTUpdateResult]:
        """
        Updates multiple fine-grained skills simultaneously based on structured test evidence.
        Prevents single overall score collapse by maintaining distinct knowledge states.
        """
        results = {}
        for skill, is_correct in evidence.items():
            prior = current_skills.get(skill, self.get_skill_params(skill).p_init)
            results[skill.value] = self.update_skill(skill, prior, is_correct)
        return results


# Global singleton instance
bkt_engine = BayesianKnowledgeTracer()

