"""
Unit tests for the Bayesian Knowledge Tracing (BKT) engine.
Verifies prior updates, probability boundaries, and transition mechanics.
"""

from app.intelligence.bkt_engine import BKTEngine


def test_bkt_correct_attempt_increases_mastery():
    """A correct attempt must increase the posterior mastery probability."""
    initial_p = 0.20
    result = BKTEngine.update_knowledge_state(
        prior_p_known=initial_p,
        is_correct=True,
    )

    assert result["next_prior_p_known"] > initial_p
    assert result["posterior_p_known"] > initial_p
    assert 0.0 <= result["next_prior_p_known"] <= 1.0


def test_bkt_incorrect_attempt_decreases_or_dampens_mastery():
    """An incorrect attempt must yield a posterior lower than the prior."""
    initial_p = 0.60
    result = BKTEngine.update_knowledge_state(
        prior_p_known=initial_p,
        is_correct=False,
    )

    assert result["posterior_p_known"] < initial_p


def test_bkt_mastery_threshold():
    """Mastery flag should be set when p_known crosses the mastery threshold."""
    result = BKTEngine.update_knowledge_state(
        prior_p_known=0.90,
        is_correct=True,
    )
    assert result["is_mastered"] is True

