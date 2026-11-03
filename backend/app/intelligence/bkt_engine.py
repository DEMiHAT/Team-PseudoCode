"""
Bayesian Knowledge Tracing (BKT) Engine.
Pure cognitive modeling component - decoupled from domain specifics.
Implements standard Corbin & Anderson (1995) Bayesian update equations.
"""

from typing import Dict, Any


class BKTEngine:
    """
    Standard Bayesian Knowledge Tracing model.
    Tracks cognitive latent knowledge state p(L) over a sequence of learning opportunities.
    """

    DEFAULT_P_INIT = 0.20   # Prior probability of knowing concept P(L_0)
    DEFAULT_P_TRANSIT = 0.15 # Probability of learning skill at step P(T)
    DEFAULT_P_GUESS = 0.15  # Probability of correct answer by guessing P(G)
    DEFAULT_P_SLIP = 0.10   # Probability of making an error despite mastery P(S)
    MASTERY_THRESHOLD = 0.85 # Mastery cutoff threshold

    @classmethod
    def update_knowledge_state(
        cls,
        prior_p_known: float,
        is_correct: bool,
        p_transit: float = DEFAULT_P_TRANSIT,
        p_guess: float = DEFAULT_P_GUESS,
        p_slip: float = DEFAULT_P_SLIP,
    ) -> Dict[str, Any]:
        """
        Updates knowledge probability using Bayes' theorem followed by transition update.

        Args:
            prior_p_known: P(L_t) - Current belief that student knows the skill.
            is_correct: Observed performance on current task (True = success, False = failure).
            p_transit: P(T) - Learning transition probability.
            p_guess: P(G) - Guess probability.
            p_slip: P(S) - Slip probability.

        Returns:
            Dictionary containing posterior_p_known, next_prior_p_known, and mastery status.
        """
        # Clamp prior into stable probability bounds (0.001 to 0.999) to avoid division by zero
        p_l = max(0.001, min(0.999, float(prior_p_known)))

        # Step 1: Compute posterior probability P(L_t | observation)
        if is_correct:
            numerator = p_l * (1.0 - p_slip)
            denominator = (p_l * (1.0 - p_slip)) + ((1.0 - p_l) * p_guess)
        else:
            numerator = p_l * p_slip
            denominator = (p_l * p_slip) + ((1.0 - p_l) * (1.0 - p_guess))

        # Safe posterior calculation
        posterior = numerator / denominator if denominator > 0 else p_l

        # Step 2: Account for learning transition towards next opportunity P(L_{t+1})
        # P(L_{t+1}) = P(L_t | obs) + (1 - P(L_t | obs)) * P(T)
        next_prior = posterior + ((1.0 - posterior) * p_transit)
        next_prior = max(0.0, min(1.0, next_prior))

        return {
            "prior_p_known": round(p_l, 4),
            "posterior_p_known": round(posterior, 4),
            "next_prior_p_known": round(next_prior, 4),
            "mastery_percentage": round(next_prior * 100.0, 1),
            "is_mastered": next_prior >= cls.MASTERY_THRESHOLD,
        }
