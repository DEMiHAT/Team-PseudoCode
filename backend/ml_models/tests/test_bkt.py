import pytest

from ml_models.bkt import (
    BayesianKnowledgeTracer,
    Skill,
    SkillParameters
)


@pytest.fixture
def bkt():
    return BayesianKnowledgeTracer()


def test_initial_mastery(bkt):
    """Each skill should start with its configured initial mastery."""

    assert bkt.get_mastery(Skill.STACK_CONCEPTUAL) == 0.25
    assert bkt.get_mastery(Skill.STACK_UNDERFLOW) == 0.15


def test_correct_answer_increases_mastery(bkt):
    """A correct answer should increase the stored mastery probability."""

    previous = bkt.get_mastery(Skill.STACK_CONCEPTUAL)

    result = bkt.update_skill(
        Skill.STACK_CONCEPTUAL,
        True
    )

    assert result.updated_probability > previous
    assert result.is_correct is True


def test_incorrect_answer_decreases_mastery(bkt):
    """An incorrect answer should reduce the stored mastery probability."""

    previous = bkt.get_mastery(Skill.STACK_CONCEPTUAL)

    result = bkt.update_skill(
        Skill.STACK_CONCEPTUAL,
        False
    )

    assert result.posterior_probability < previous
    assert result.is_correct is False


def test_mastery_percentage(bkt):
    """Mastery percentage should match the updated probability."""

    result = bkt.update_skill(
        Skill.STACK_CONCEPTUAL,
        True
    )

    assert result.mastery_percentage == round(
        result.updated_probability * 100,
        2
    )


def test_mastery_detection():
    """A sufficiently high probability should trigger mastery."""

    parameters = {
        Skill.STACK_CONCEPTUAL: SkillParameters(
            p_init=0.95,
            p_learn=0.10,
            p_guess=0.15,
            p_slip=0.10,
            mastery_threshold=0.85
        )
    }

    engine = BayesianKnowledgeTracer(parameters)

    result = engine.update_skill(
        Skill.STACK_CONCEPTUAL,
        True
    )

    assert result.is_mastered is True


def test_independent_skill_tracking(bkt):
    """Updating one skill must not change another skill."""

    initial_underflow = bkt.get_mastery(Skill.STACK_UNDERFLOW)

    bkt.update_skill(
        Skill.STACK_CONCEPTUAL,
        True
    )

    assert bkt.get_mastery(Skill.STACK_UNDERFLOW) == initial_underflow


def test_reset_skill(bkt):
    """Resetting a skill should restore its initial probability."""

    bkt.update_skill(Skill.STACK_CONCEPTUAL, True)

    bkt.reset_skill(Skill.STACK_CONCEPTUAL)

    assert bkt.get_mastery(Skill.STACK_CONCEPTUAL) == 0.25


def test_invalid_probability():
    """Invalid BKT parameters should be rejected."""

    with pytest.raises(ValueError):
        SkillParameters(p_init=1.5)


def test_invalid_skill(bkt):
    """Unknown skills should be rejected."""

    with pytest.raises(ValueError):
        bkt.update_skill("unknown_skill", True)


def test_invalid_answer_type(bkt):
    """Answers must be boolean values."""

    with pytest.raises(TypeError):
        bkt.update_skill(Skill.STACK_CONCEPTUAL, "correct")