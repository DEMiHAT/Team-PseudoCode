"""
Intervention Outcome Logging Module.
Tracks the end-to-end lifecycle and pedagogical efficacy of delivered interventions.
Calculates reward signals ready for Contextual Bandit optimization (e.g. LinUCB).
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class InterventionLifecycleRecord(BaseModel):
    """Logs an intervention event from initiation through subsequent student outcome."""
    intervention_id: str
    student_id: int
    activity_id: int
    target_skill: str
    scaffolding_tier: int  # 0 to 5
    trigger_reason: str
    decision_rationale: str

    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    subsequent_attempt_id: Optional[int] = None
    subsequent_attempt_passed: Optional[bool] = None
    subsequent_attempt_independent: Optional[bool] = None
    efficacy_score: Optional[float] = None  # -1.0 to +1.0 normalized reward
    evaluated_at: Optional[datetime] = None


class InterventionOutcomeLogger:
    """
    Evaluates and records pedagogical intervention outcomes.
    Calculates bandit reward signals:
      - Independent success on subsequent attempt -> High Efficacy (+1.0)
      - Assisted success on subsequent attempt     -> Moderate Efficacy (+0.5)
      - Persistent failure despite intervention   -> Negative Efficacy (-0.5)
    """

    @classmethod
    def record_outcome(
        cls,
        intervention: InterventionLifecycleRecord,
        attempt_id: int,
        is_passed: bool,
        was_assisted: bool,
    ) -> InterventionLifecycleRecord:
        """
        Closes the feedback loop by scoring the intervention's pedagogical impact.
        """
        intervention.subsequent_attempt_id = attempt_id
        intervention.subsequent_attempt_passed = is_passed
        intervention.subsequent_attempt_independent = not was_assisted
        intervention.evaluated_at = datetime.now(timezone.utc)

        # Calculate normalized efficacy score (reward signal for contextual bandit policy)
        if is_passed and not was_assisted:
            # Optimal outcome: Student attained independent mastery
            intervention.efficacy_score = 1.0
        elif is_passed and was_assisted:
            # Positive outcome: Student succeeded with ongoing scaffolding
            intervention.efficacy_score = 0.5
        else:
            # Suboptimal outcome: Student remains stuck despite hint
            intervention.efficacy_score = -0.5

        return intervention


outcome_logger = InterventionOutcomeLogger()

