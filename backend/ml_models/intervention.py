"""
Intervention Selection Model

Selects the most suitable learning support based on:
- Student mastery level
- Diagnosed programming errors
- Repeated mistakes
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class InterventionType(str, Enum):
    HINT = "hint"
    EXPLANATION = "explanation"
    VISUALIZATION = "visualization"
    WORKED_EXAMPLE = "worked_example"
    PRACTICE = "practice"


@dataclass
class InterventionResult:
    intervention: InterventionType
    reason: str
    priority: str
    mastery_percentage: float


class InterventionSelector:

    def select(
        self,
        mastery_probability: float,
        error_category: Optional[str] = None,
        repeated_errors: int = 0,
    ) -> InterventionResult:
        """
        Select a learning intervention.

        mastery_probability: Value between 0.0 and 1.0.
        error_category: Category returned by the error diagnosis model.
        repeated_errors: Number of repeated errors.
        """

        if not isinstance(mastery_probability, (int, float)):
            raise TypeError("mastery_probability must be a number")

        if not 0.0 <= mastery_probability <= 1.0:
            raise ValueError(
                "mastery_probability must be between 0.0 and 1.0"
            )

        if error_category is not None and not isinstance(error_category, str):
            raise TypeError("error_category must be a string or None")

        if not isinstance(repeated_errors, int) or isinstance(repeated_errors, bool):
            raise TypeError("repeated_errors must be an integer")

        if repeated_errors < 0:
            raise ValueError("repeated_errors cannot be negative")

        mastery_percentage = round(mastery_probability * 100, 2)
        category = (error_category or "").strip().lower()

        # Repeated errors need more guided support.
        if repeated_errors >= 3:
            return InterventionResult(
                intervention=InterventionType.WORKED_EXAMPLE,
                reason="Repeated errors detected. A step-by-step worked example is recommended.",
                priority="high",
                mastery_percentage=mastery_percentage,
            )

        # Match specific errors with suitable interventions.
        if category in ("lifo_misconception", "parentheses_validation"):
            return InterventionResult(
                intervention=InterventionType.VISUALIZATION,
                reason="A visual representation can help clarify this concept.",
                priority="high",
                mastery_percentage=mastery_percentage,
            )

        if category in ("stack_underflow", "stack_overflow"):
            return InterventionResult(
                intervention=InterventionType.EXPLANATION,
                reason="The student needs clarification of stack operation conditions.",
                priority="high",
                mastery_percentage=mastery_percentage,
            )

        if category in ("compilation", "null_pointer", "array_index"):
            return InterventionResult(
                intervention=InterventionType.HINT,
                reason="A targeted hint can guide the student toward correcting the error.",
                priority="medium",
                mastery_percentage=mastery_percentage,
            )

        if category == "logical":
            return InterventionResult(
                intervention=InterventionType.HINT,
                reason="A hint can help the student identify the logical mistake.",
                priority="medium",
                mastery_percentage=mastery_percentage,
            )

        # General intervention based on mastery.
        if mastery_probability < 0.40:
            return InterventionResult(
                intervention=InterventionType.EXPLANATION,
                reason="Low mastery detected. Explain the concept from the basics.",
                priority="high",
                mastery_percentage=mastery_percentage,
            )

        if mastery_probability < 0.70:
            return InterventionResult(
                intervention=InterventionType.WORKED_EXAMPLE,
                reason="Developing mastery. A guided example can strengthen understanding.",
                priority="medium",
                mastery_percentage=mastery_percentage,
            )

        if mastery_probability < 0.85:
            return InterventionResult(
                intervention=InterventionType.PRACTICE,
                reason="The student is progressing. Additional practice can reinforce learning.",
                priority="medium",
                mastery_percentage=mastery_percentage,
            )

        return InterventionResult(
            intervention=InterventionType.PRACTICE,
            reason="Strong mastery detected. Continue with challenging practice.",
            priority="low",
            mastery_percentage=mastery_percentage,
        )


# Shared selector instance
intervention_selector = InterventionSelector()