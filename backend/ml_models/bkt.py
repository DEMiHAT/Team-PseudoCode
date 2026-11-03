"""
Bayesian Knowledge Tracing (BKT)
Model 1 - Adaptive DSA Learning System

Purpose:
Estimate a student's mastery of individual DSA concepts
and update the estimated mastery after each attempt.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Union


# ---------------------------------------------------------
# 1. DSA SKILLS
# ---------------------------------------------------------

class Skill(str, Enum):
    STACK_CONCEPTUAL = "stack_conceptual"
    STACK_JAVA_IMPLEMENTATION = "stack_java_implementation"
    STACK_UNDERFLOW = "stack_underflow"
    PARENTHESES_VALIDATION = "parentheses_validation"


# ---------------------------------------------------------
# 2. BKT PARAMETERS
# ---------------------------------------------------------

@dataclass(frozen=True)
class SkillParameters:
    """
    Parameters used by Bayesian Knowledge Tracing.

    p_init: Initial probability that the student knows the skill.
    p_learn: Probability of learning the skill after an attempt.
    p_guess: Probability of answering correctly without knowing.
    p_slip: Probability of answering incorrectly despite knowing.
    mastery_threshold: Probability required to consider a skill mastered.
    """

    p_init: float = 0.20
    p_learn: float = 0.15
    p_guess: float = 0.15
    p_slip: float = 0.10
    mastery_threshold: float = 0.85

    def __post_init__(self):
        for name in ("p_init", "p_learn", "p_guess", "p_slip"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")

        if not 0.5 <= self.mastery_threshold <= 1.0:
            raise ValueError(
                "mastery_threshold must be between 0.5 and 1.0"
            )


# ---------------------------------------------------------
# 3. DEFAULT PARAMETERS FOR EACH SKILL
# ---------------------------------------------------------

DEFAULT_SKILL_PARAMETERS: Dict[Skill, SkillParameters] = {
    Skill.STACK_CONCEPTUAL: SkillParameters(
        p_init=0.25,
        p_learn=0.18,
        p_guess=0.20,
        p_slip=0.08,
        mastery_threshold=0.85
    ),

    Skill.STACK_JAVA_IMPLEMENTATION: SkillParameters(
        p_init=0.20,
        p_learn=0.15,
        p_guess=0.15,
        p_slip=0.12,
        mastery_threshold=0.85
    ),

    Skill.STACK_UNDERFLOW: SkillParameters(
        p_init=0.15,
        p_learn=0.20,
        p_guess=0.10,
        p_slip=0.10,
        mastery_threshold=0.85
    ),

    Skill.PARENTHESES_VALIDATION: SkillParameters(
        p_init=0.20,
        p_learn=0.14,
        p_guess=0.12,
        p_slip=0.10,
        mastery_threshold=0.85
    )
}


# ---------------------------------------------------------
# 4. BKT RESULT
# ---------------------------------------------------------

@dataclass
class BKTResult:
    skill_name: str
    is_correct: bool
    prior_probability: float
    posterior_probability: float
    updated_probability: float
    mastery_percentage: float
    is_mastered: bool


# ---------------------------------------------------------
# 5. BAYESIAN KNOWLEDGE TRACING ENGINE
# ---------------------------------------------------------

class BayesianKnowledgeTracer:

    def __init__(
        self,
        skill_parameters: Dict[Skill, SkillParameters] = None
    ):
        self.skill_parameters = (
            skill_parameters or DEFAULT_SKILL_PARAMETERS.copy()
        )

        self.mastery: Dict[Skill, float] = {
            skill: params.p_init
            for skill, params in self.skill_parameters.items()
        }

    @staticmethod
    def _validate_probability(value: float, name: str):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number")

        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be between 0 and 1")

    def get_mastery(self, skill: Union[Skill, str]) -> float:
        skill = Skill(skill)

        if skill not in self.mastery:
            raise ValueError(f"No parameters configured for {skill.value}")

        return self.mastery[skill]

    def update_skill(
        self,
        skill: Union[Skill, str],
        is_correct: bool
    ) -> BKTResult:

        skill = Skill(skill)

        if skill not in self.skill_parameters:
            raise ValueError(f"No parameters configured for {skill.value}")

        if not isinstance(is_correct, bool):
            raise TypeError("is_correct must be a boolean")

        params = self.skill_parameters[skill]
        prior = self.mastery[skill]

        # -------------------------------------------------
        # Step A: Calculate probability after observing answer
        # -------------------------------------------------

        if is_correct:
            numerator = prior * (1 - params.p_slip)

            denominator = (
                numerator
                + (1 - prior) * params.p_guess
            )

        else:
            numerator = prior * params.p_slip

            denominator = (
                numerator
                + (1 - prior) * (1 - params.p_guess)
            )

        # Handle mathematically impossible evidence.
        if denominator == 0:
            posterior = prior
        else:
            posterior = numerator / denominator

        # -------------------------------------------------
        # Step B: Apply learning transition
        # -------------------------------------------------

        updated_probability = (
            posterior
            + (1 - posterior) * params.p_learn
        )

        # -------------------------------------------------
        # Step C: Update stored learner mastery
        # -------------------------------------------------

        self.mastery[skill] = updated_probability

        # -------------------------------------------------
        # Step D: Check mastery threshold
        # -------------------------------------------------

        mastery_percentage = updated_probability * 100

        is_mastered = (
            updated_probability >= params.mastery_threshold
        )

        return BKTResult(
            skill_name=skill.value,
            is_correct=is_correct,
            prior_probability=round(prior, 4),
            posterior_probability=round(posterior, 4),
            updated_probability=round(updated_probability, 4),
            mastery_percentage=round(mastery_percentage, 2),
            is_mastered=is_mastered
        )

    def get_all_mastery(self) -> Dict[str, float]:
        return {
            skill.value: round(probability, 4)
            for skill, probability in self.mastery.items()
        }

    def reset_skill(self, skill: Union[Skill, str]):
        skill = Skill(skill)

        if skill not in self.skill_parameters:
            raise ValueError(f"No parameters configured for {skill.value}")

        self.mastery[skill] = self.skill_parameters[skill].p_init

    def reset_all(self):
        for skill, params in self.skill_parameters.items():
            self.mastery[skill] = params.p_init


# ---------------------------------------------------------
# 6. DEFAULT ENGINE INSTANCE
# ---------------------------------------------------------

bkt_engine = BayesianKnowledgeTracer()