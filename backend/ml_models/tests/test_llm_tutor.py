import pytest

from ml_models.llm_tutor import (
    LLMTutor,
    TutorError,
    TutorResponse,
)


class MockGeminiResponse:
    def __init__(self, text):
        self.text = text


class MockModels:
    def generate_content(self, model, contents):
        return MockGeminiResponse(
            "This is a sample tutor response."
        )


class MockClient:
    def __init__(self):
        self.models = MockModels()


@pytest.fixture
def tutor():
    instance = LLMTutor(api_key="test-api-key")
    instance.client = MockClient()
    return instance


def test_generate_explanation(tutor):
    result = tutor.generate_explanation(
        concept="Stack",
        mastery_percentage=30,
    )

    assert isinstance(result, TutorResponse)
    assert result.response_type == "explanation"
    assert "sample tutor response" in result.response


def test_generate_hint(tutor):
    result = tutor.generate_hint(
        question="What is stack underflow?",
        student_code="stack.pop();",
    )

    assert result.response_type == "hint"
    assert result.response


def test_explain_error(tutor):
    result = tutor.explain_error(
        code="stack.pop();",
        error_category="stack_underflow",
        error_details="EmptyStackException",
    )

    assert result.response_type == "error_explanation"
    assert result.response


def test_generate_step_by_step(tutor):
    result = tutor.generate_step_by_step(
        question="Explain stack implementation in Java.",
        mastery_percentage=50,
    )

    assert result.response_type == "step_by_step"
    assert result.response


def test_response_contains_model_name(tutor):
    result = tutor.generate_explanation("Stack")

    assert result.model == "gemini-2.5-flash"


def test_missing_api_key():
    instance = LLMTutor(api_key="")

    assert instance.client is None

    with pytest.raises(TutorError):
        instance.generate_explanation("Stack")


def test_invalid_mastery_type(tutor):
    with pytest.raises(TypeError):
        tutor.generate_explanation(
            "Stack",
            mastery_percentage="high",
        )


def test_invalid_mastery_range(tutor):
    with pytest.raises(ValueError):
        tutor.generate_explanation(
            "Stack",
            mastery_percentage=120,
        )


def test_empty_gemini_response(tutor):
    class EmptyModels:
        def generate_content(self, model, contents):
            return MockGeminiResponse("")

    class EmptyClient:
        def __init__(self):
            self.models = EmptyModels()

    tutor.client = EmptyClient()

    with pytest.raises(TutorError):
        tutor.generate_explanation("Stack")


def test_gemini_api_failure(tutor):
    class FailingModels:
        def generate_content(self, model, contents):
            raise RuntimeError("Simulated API failure")

    class FailingClient:
        def __init__(self):
            self.models = FailingModels()

    tutor.client = FailingClient()

    with pytest.raises(TutorError):
        tutor.generate_explanation("Stack")