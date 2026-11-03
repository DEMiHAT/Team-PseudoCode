"""
Adaptive Intervention Selector.
Determines optimal pedagogical intervention based on student mastery level, attempt streak, and diagnostics.
"""

from typing import Dict, Any, List


class AdaptiveInterventionSelector:
    """
    Selects the most suitable cognitive intervention.
    Maps student state to pedagogical strategies:
      - High mastery (>= 0.70) + First failure: Mild Tier 1 hint (invariants)
      - Medium mastery (0.40 - 0.70) + Repeated failure: Tier 2 algorithmic pseudocode
      - Low mastery (< 0.40) or repeated errors (>= 3): Tier 3 dry run trace or Tier 4 skeleton
    """

    @classmethod
    def select_intervention(
        cls,
        consecutive_failures: int,
        p_known: float,
        has_compilation_error: bool,
        has_runtime_error: bool,
        misconceptions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculates recommended scaffolding tier and pedagogical action.
        """
        # Scenario A: Compilation error dominates
        if has_compilation_error:
            return {
                "recommended_tier": 1,
                "strategy": "Syntax & Interface Correction",
                "trigger_reason": "Compilation Failure",
                "message": "Focus on the compiler diagnostic first before adjusting the core algorithm.",
            }

        # Scenario B: Critical runtime misconception diagnosed (e.g. infinite recursion, null pointer)
        critical_misconceptions = [m for m in misconceptions if m.get("severity") == "Critical"]
        if critical_misconceptions:
            return {
                "recommended_tier": 2,
                "strategy": "Targeted Bug Remediation",
                "trigger_reason": f"Diagnosed {critical_misconceptions[0]['name']}",
                "message": critical_misconceptions[0]["suggested_remedy"],
            }

        # Scenario C: Struggling student with repeated failures (3+ attempts)
        if consecutive_failures >= 3:
            return {
                "recommended_tier": 3 if p_known > 0.3 else 4,
                "strategy": "Concrete Trace & Scaffolding",
                "trigger_reason": "Persistent Impasse (3+ incorrect attempts)",
                "message": "Step through execution states or review the scaffolded logic skeleton.",
            }

        # Scenario D: Second failure
        if consecutive_failures == 2:
            return {
                "recommended_tier": 2,
                "strategy": "Algorithmic Invariant Check",
                "trigger_reason": "Second incorrect attempt",
                "message": "Revisit the pseudocode loop invariants and pointer movements.",
            }

        # Scenario E: First failure or exploratory attempt
        return {
            "recommended_tier": 1,
            "strategy": "Reflective Prompting",
            "trigger_reason": "Initial test case discrepancy",
            "message": "Consider the edge case boundaries (empty collection, single element, negative keys).",
        }
