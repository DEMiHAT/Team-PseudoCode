import pytest

from ml_models.error_diagnosis import (
    ProgrammingErrorDiagnoser,
    ErrorCategory,
    Severity
)


@pytest.fixture
def diagnoser():
    return ProgrammingErrorDiagnoser()


def test_compilation_error(diagnoser):
    results = diagnoser.diagnose(
        compile_output="error: ';' expected"
    )

    assert results[0].category == ErrorCategory.COMPILATION
    assert results[0].severity == Severity.HIGH


def test_stack_underflow(diagnoser):
    results = diagnoser.diagnose(
        runtime_output="java.util.EmptyStackException"
    )

    assert any(
        r.category == ErrorCategory.STACK_UNDERFLOW
        for r in results
    )


def test_stack_overflow(diagnoser):
    results = diagnoser.diagnose(
        runtime_output="Stack overflow: stack capacity exceeded"
    )

    assert any(
        r.category == ErrorCategory.STACK_OVERFLOW
        for r in results
    )


def test_lifo_misconception(diagnoser):
    results = diagnoser.diagnose(
        test_failures=["Expected LIFO order but got FIFO"]
    )

    assert any(
        r.category == ErrorCategory.LIFO_MISCONCEPTION
        for r in results
    )


def test_parentheses_validation(diagnoser):
    results = diagnoser.diagnose(
        test_failures=["Unbalanced parentheses detected"]
    )

    assert any(
        r.category == ErrorCategory.PARENTHESES_VALIDATION
        for r in results
    )


def test_null_pointer_error(diagnoser):
    results = diagnoser.diagnose(
        runtime_output="java.lang.NullPointerException"
    )

    assert any(
        r.category == ErrorCategory.NULL_POINTER
        for r in results
    )


def test_array_index_error(diagnoser):
    results = diagnoser.diagnose(
        runtime_output="ArrayIndexOutOfBoundsException: Index 5"
    )

    assert any(
        r.category == ErrorCategory.ARRAY_INDEX
        for r in results
    )


def test_logical_error(diagnoser):
    results = diagnoser.diagnose(
        test_failures=["Expected output 10 but received 5"]
    )

    assert any(
        r.category == ErrorCategory.LOGICAL
        for r in results
    )


def test_unknown_error(diagnoser):
    results = diagnoser.diagnose()

    assert len(results) == 1
    assert results[0].category == ErrorCategory.UNKNOWN


def test_diagnostic_explanation(diagnoser):
    results = diagnoser.diagnose(
        runtime_output="EmptyStackException"
    )

    result = results[0]

    assert result.title
    assert result.explanation
    assert result.evidence
    assert result.suggested_action
    assert 0.0 <= result.confidence <= 1.0


def test_misconception_identification(diagnoser):
    results = diagnoser.diagnose(
        runtime_output="EmptyStackException"
    )

    result = next(
        r for r in results
        if r.category == ErrorCategory.STACK_UNDERFLOW
    )

    assert result.misconception is True


def test_invalid_input_type(diagnoser):
    with pytest.raises(TypeError):
        diagnoser.diagnose(
            compile_output=123
        )


def test_invalid_test_failures_type(diagnoser):
    with pytest.raises(TypeError):
        diagnoser.diagnose(
            test_failures="not a list"
        )


def test_multiple_errors(diagnoser):
    results = diagnoser.diagnose(
        runtime_output=(
            "EmptyStackException\n"
            "NullPointerException"
        )
    )

    categories = [r.category for r in results]

    assert ErrorCategory.STACK_UNDERFLOW in categories
    assert ErrorCategory.NULL_POINTER in categories


def test_no_duplicate_logical_error(diagnoser):
    results = diagnoser.diagnose(
        test_failures=["EmptyStackException"]
    )

    categories = [r.category for r in results]

    assert ErrorCategory.STACK_UNDERFLOW in categories
    assert ErrorCategory.LOGICAL not in categories