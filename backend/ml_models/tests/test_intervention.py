import pytest

from ml_models.intervention import (
    InterventionSelector,
    InterventionType,
)


@pytest.fixture
def selector():
    return InterventionSelector()


def test_low_mastery_selects_explanation(selector):
    result = selector.select(0.20)

    assert result.intervention == InterventionType.EXPLANATION
    assert result.priority == "high"


def test_medium_mastery_selects_worked_example(selector):
    result = selector.select(0.55)

    assert result.intervention == InterventionType.WORKED_EXAMPLE


def test_developing_mastery_selects_practice(selector):
    result = selector.select(0.75)

    assert result.intervention == InterventionType.PRACTICE


def test_high_mastery_selects_practice(selector):
    result = selector.select(0.95)

    assert result.intervention == InterventionType.PRACTICE
    assert result.priority == "low"


def test_lifo_error_selects_visualization(selector):
    result = selector.select(
        0.60,
        error_category="lifo_misconception",
    )

    assert result.intervention == InterventionType.VISUALIZATION


def test_parentheses_error_selects_visualization(selector):
    result = selector.select(
        0.60,
        error_category="parentheses_validation",
    )

    assert result.intervention == InterventionType.VISUALIZATION


def test_underflow_error_selects_explanation(selector):
    result = selector.select(
        0.60,
        error_category="stack_underflow",
    )

    assert result.intervention == InterventionType.EXPLANATION


def test_overflow_error_selects_explanation(selector):
    result = selector.select(
        0.60,
        error_category="stack_overflow",
    )

    assert result.intervention == InterventionType.EXPLANATION


def test_compilation_error_selects_hint(selector):
    result = selector.select(
        0.60,
        error_category="compilation",
    )

    assert result.intervention == InterventionType.HINT


def test_logical_error_selects_hint(selector):
    result = selector.select(
        0.60,
        error_category="logical",
    )

    assert result.intervention == InterventionType.HINT


def test_repeated_errors_select_worked_example(selector):
    result = selector.select(
        0.70,
        error_category="logical",
        repeated_errors=3,
    )

    assert result.intervention == InterventionType.WORKED_EXAMPLE
    assert result.priority == "high"


def test_repeated_errors_take_priority(selector):
    result = selector.select(
        0.20,
        error_category="compilation",
        repeated_errors=3,
    )

    assert result.intervention == InterventionType.WORKED_EXAMPLE


def test_mastery_percentage(selector):
    result = selector.select(0.75)

    assert result.mastery_percentage == 75.0


def test_invalid_mastery_probability(selector):
    with pytest.raises(ValueError):
        selector.select(1.5)


def test_invalid_mastery_type(selector):
    with pytest.raises(TypeError):
        selector.select("0.75")


def test_negative_repeated_errors(selector):
    with pytest.raises(ValueError):
        selector.select(0.50, repeated_errors=-1)


def test_invalid_repeated_errors_type(selector):
    with pytest.raises(TypeError):
        selector.select(0.50, repeated_errors=1.5)