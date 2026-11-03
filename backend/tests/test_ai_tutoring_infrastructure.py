"""
Comprehensive Test Suite for AI Tutoring Infrastructure (IT22301 DSA).
Validates Gemini client resilience, context retrieval, learner-state integration,
prompt templates, teaching guardrails, deterministic fallbacks, and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.ai_tutor.schemas import TutorContext, CodeExecutionEvidence, HintRequest, ErrorExplanationRequest, ConceptSimplificationRequest, PracticeQuestionRequest
from app.ai_tutor.gemini_client import GeminiClient
from app.ai_tutor.context_retriever import ContextRetriever
from app.ai_tutor.learner_state_bridge import LearnerStateBridge
from app.ai_tutor.prompt_templates import (
    SYSTEM_TEACHING_INSTRUCTION,
    build_hint_prompt,
    build_error_explanation_prompt,
    build_concept_simplification_prompt,
    build_practice_question_prompt,
)
from app.ai_tutor.response_validator import ResponseValidator
from app.ai_tutor.orchestrator import TutorOrchestrator


client = TestClient(app)


# ==========================================
# 1. Gemini Client Tests
# ==========================================
def test_gemini_client_unconfigured_state():
    """Client handles empty API key gracefully without raising unexpected exceptions."""
    unconfigured_client = GeminiClient(api_key="")
    assert not unconfigured_client.is_configured


@pytest.mark.asyncio
async def test_gemini_client_health_check_when_unconfigured():
    """Health check reports unconfigured status when API key is missing."""
    unconfigured_client = GeminiClient(api_key="")
    health = await unconfigured_client.check_health()
    assert health["status"] == "unconfigured"
    assert not health["is_healthy"]
    assert "deterministic fallback" in health["message"]


@pytest.mark.asyncio
async def test_gemini_client_generate_content_when_unconfigured():
    """generate_content returns unconfigured flag when API key is missing."""
    unconfigured_client = GeminiClient(api_key="")
    result = await unconfigured_client.generate_content("Explain stacks")
    assert not result["success"]
    assert result["is_unconfigured"]
    assert "Gemini API key is not configured" in result["error"]


# ==========================================
# 2. Context Retrieval & Learner-State Tests
# ==========================================
def test_context_retriever_builds_complete_context():
    """ContextRetriever gathers all required context variables."""
    retriever = ContextRetriever()
    evidence = CodeExecutionEvidence(
        has_evidence=True,
        status="Runtime Error",
        stderr="java.util.EmptyStackException at Stack.pop(Stack.java:14)",
    )
    ctx = retriever.build_context(
        student_id=101,
        scaffold_level=2,
        current_code="class MyStack { int pop() { return s.pop(); } }",
        execution_evidence=evidence,
    )

    assert ctx.student_id == 101
    assert "IT22301" in ctx.subject
    assert ctx.topic == "Stacks"
    assert ctx.scaffold_level == 2
    assert ctx.execution_evidence.has_evidence
    assert "EmptyStackException" in ctx.execution_evidence.stderr
    assert len(ctx.estimated_mastery) > 0


def test_learner_state_bridge_proficiency_categorization():
    """Proficiency levels are mapped correctly from BKT mastery probabilities."""
    assert LearnerStateBridge._calculate_proficiency_label(0.90) == "Mastered"
    assert LearnerStateBridge._calculate_proficiency_label(0.70) == "Competent"
    assert LearnerStateBridge._calculate_proficiency_label(0.50) == "Developing"
    assert LearnerStateBridge._calculate_proficiency_label(0.25) == "Novice"


# ==========================================
# 3. Prompt Template Guardrails
# ==========================================
def test_prompt_templates_embed_pedagogical_rules():
    """Prompt templates include critical teaching rules."""
    ctx = TutorContext(
        student_id=1,
        topic="Stacks",
        scaffold_level=1,
        current_code="int pop() { return array[top--]; }",
    )

    hint_prompt = build_hint_prompt(ctx)
    assert "Assistance Level: 1" in hint_prompt
    assert "ONE actionable hint" in hint_prompt
    assert "Conclude with an explicit prompt" in hint_prompt

    error_prompt = build_error_explanation_prompt(
        context=ctx,
        compiler_error="';' expected at line 14",
    )
    assert "ACTUAL VERIFIED ERROR EVIDENCE" in error_prompt
    assert "';' expected at line 14" in error_prompt
    assert "Do NOT rewrite the student's entire method" in error_prompt

    concept_prompt = build_concept_simplification_prompt(
        context=ctx,
        concept_name="Monotonic Stack",
    )
    assert "Monotonic Stack" in concept_prompt
    assert "Java code snippet" in concept_prompt

    practice_prompt = build_practice_question_prompt(
        context=ctx,
        target_concept="stack_underflow",
        difficulty="Intermediate",
    )
    assert "strict JSON" in practice_prompt
    assert "stack_underflow" in practice_prompt


# ==========================================
# 4. Response Validator & Guardrails
# ==========================================
def test_response_validator_sanitizes_complete_solution_on_scaffold_below_5():
    """Prevents premature full solution dumps on lower scaffolding levels."""
    leaked_solution = (
        "Here is what you need to do:\n"
        "public class StackSolution { public int pop() { return 42; } }\n"
        "Try understanding this."
    )
    response = ResponseValidator.validate_and_format_hint(
        llm_text=leaked_solution,
        scaffold_level=2,
        pedagogical_strategy="Targeted Hint",
    )
    assert response.success
    assert "public class StackSolution" not in response.content
    assert "[Complete class omitted" in response.content
    assert response.actionable_next_step is not None


def test_response_validator_practice_question_json_parsing():
    """Cleans markdown JSON fences and validates practice question schema."""
    markdown_json = """```json
    [
      {
        "question_id": "PQ-TEST-01",
        "prompt": "What happens when an empty stack is popped?",
        "options": [
          {"id": "A", "text": "Returns 0"},
          {"id": "B", "text": "Throws EmptyStackException"}
        ],
        "correct_option_id": "B",
        "explanation": "Calling pop() without checking isEmpty() throws EmptyStackException.",
        "target_skill": "stack_underflow",
        "difficulty": "Beginner"
      }
    ]
    ```"""
    parsed = ResponseValidator.validate_and_format_practice_questions(
        llm_text=markdown_json,
        target_concept="stack_underflow",
    )
    assert parsed.success
    assert not parsed.is_fallback
    assert len(parsed.questions) == 1
    assert parsed.questions[0].correct_option_id == "B"


# ==========================================
# 5. Deterministic Fallbacks (Zero Downtime)
# ==========================================
def test_fallback_hint_generation():
    """Provides high-quality deterministic scaffolding when Gemini is unavailable."""
    fallback = ResponseValidator.get_fallback_hint(scaffold_level=1)
    assert fallback.is_fallback
    assert "LIFO" in fallback.content or "reflect" in fallback.content.lower()
    assert fallback.actionable_next_step is not None


def test_fallback_error_explanation():
    """Provides deterministic error diagnosis when Gemini is unavailable."""
    fallback = ResponseValidator.get_fallback_error_explanation(
        runtime_error="EmptyStackException"
    )
    assert fallback.is_fallback
    assert "isEmpty()" in fallback.content
    assert fallback.actionable_next_step is not None


def test_fallback_practice_questions():
    """Provides deterministic practice questions when Gemini is unavailable."""
    fallback = ResponseValidator.get_fallback_practice_questions(target_concept="Stacks")
    assert fallback.is_fallback
    assert len(fallback.questions) >= 1
    assert fallback.questions[0].options[0].id == "A"


# ==========================================
# 6. Tutor Orchestration Service
# ==========================================
@pytest.mark.asyncio
async def test_orchestrator_scaffolded_hint_fallback():
    """Orchestrator generates hint using fallback engine when Gemini is unconfigured."""
    unconfigured_client = GeminiClient(api_key="")
    orchestrator = TutorOrchestrator(client=unconfigured_client)
    req = HintRequest(
        student_id=1,
        scaffold_level=1,
        current_code="class Stack { }",
    )
    response = await orchestrator.provide_scaffolded_hint(request=req, db=None)
    assert response.success
    assert response.is_fallback
    assert response.scaffold_level == 1
    assert response.actionable_next_step is not None


@pytest.mark.asyncio
async def test_orchestrator_explain_error_with_mock_llm():
    """Orchestrator coordinates error explanation with mocked LLM response."""
    mock_client = GeminiClient(api_key="mock_key")
    mock_client.generate_content = AsyncMock(return_value={
        "success": True,
        "text": "The error occurs because you popped without checking isEmpty(). Try adding a guard check.",
        "raw_response": {},
        "error": None,
        "is_unconfigured": False,
    })

    orchestrator = TutorOrchestrator(client=mock_client)
    req = ErrorExplanationRequest(
        student_id=1,
        code="int x = s.pop();",
        runtime_error="EmptyStackException at line 1",
    )
    response = await orchestrator.explain_code_error(request=req, db=None)
    assert response.success
    assert not response.is_fallback
    assert "isEmpty()" in response.content
    assert response.actionable_next_step is not None


# ==========================================
# 7. FastAPI Route Endpoints
# ==========================================
def test_api_tutoring_health_endpoint():
    """Verifies GET /api/v1/tutoring/health returns operational status."""
    res = client.get("/api/v1/tutoring/health")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "orchestrator_status" in data["data"]


def test_api_tutoring_hint_endpoint():
    """Verifies POST /api/v1/tutoring/hint produces a scaffolded hint."""
    payload = {
        "student_id": 1,
        "scaffold_level": 1,
        "current_code": "public class Solution { }",
    }
    res = client.post("/api/v1/tutoring/hint", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["scaffold_level"] == 1
    assert "content" in data["data"]
    assert "actionable_next_step" in data["data"]


def test_api_tutoring_explain_error_endpoint():
    """Verifies POST /api/v1/tutoring/explain-error explains runtime exception."""
    payload = {
        "student_id": 1,
        "code": "int top = stack.pop();",
        "runtime_error": "java.util.EmptyStackException",
    }
    res = client.post("/api/v1/tutoring/explain-error", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "content" in data["data"]


def test_api_tutoring_simplify_concept_endpoint():
    """Verifies POST /api/v1/tutoring/simplify-concept delivers analogical explanation."""
    payload = {
        "student_id": 1,
        "concept_name": "LIFO Principle",
        "student_question": "Why is it called Last-In First-Out?",
    }
    res = client.post("/api/v1/tutoring/simplify-concept", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "content" in data["data"]


def test_api_tutoring_practice_questions_endpoint():
    """Verifies POST /api/v1/tutoring/practice-questions returns formative questions."""
    payload = {
        "student_id": 1,
        "target_concept": "stack_underflow",
        "difficulty": "Beginner",
        "count": 2,
    }
    res = client.post("/api/v1/tutoring/practice-questions", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]["questions"]) >= 1
    assert data["data"]["questions"][0]["target_skill"] != ""
