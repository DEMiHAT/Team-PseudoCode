"""
Unit and Integration Tests for Code Execution Infrastructure.
Validates Judge0 CE client, execution routes, compilation/runtime error handling,
Valid Parentheses benchmark exercise, DB attempt/submission storage, and BKT state updates.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.activity import Activity
from app.models.attempt import Attempt
from app.models.code_submission import CodeSubmission
from app.models.execution_result import ExecutionResult
from app.models.learner_skill_state import LearnerSkillState
from app.services.judge0_service import Judge0ServiceClient, DEFAULT_JAVA_LANGUAGE_ID


client = TestClient(app)


# ==========================================
# 1. Judge0 Integration Service Tests
# ==========================================
def test_judge0_client_configuration():
    """Validates Judge0 client parameters, headers, and language ID."""
    svc = Judge0ServiceClient(
        api_url="http://localhost:2358",
        api_key="",
        timeout_seconds=5.0,
    )
    assert svc.api_url == "http://localhost:2358"
    assert svc.default_time_limit_sec == 4.0
    assert svc.default_memory_limit_kb == 128000
    headers = svc._get_headers()
    assert headers["Content-Type"] == "application/json"
    assert "X-RapidAPI-Key" not in headers


@pytest.mark.asyncio
async def test_judge0_client_offline_graceful_handling():
    """Client returns structured offline failure dictionary when Judge0 is unreachable."""
    svc = Judge0ServiceClient(api_url="http://invalid-host-2358.local")
    health = await svc.check_health()
    assert not health["is_healthy"]
    assert health["status"] == "offline"

    # Execution attempt returns clear offline notice without raising uncaught exceptions
    res = await svc.execute_java_code(
        source_code="public class Main { public static void main(String[] args) {} }",
        stdin_input="",
    )
    assert not res["is_passed"]
    assert res["status"] == "Execution Server Offline"
    assert res["error_type"] == "SERVICE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_judge0_client_compilation_error_classification():
    """Judge0 status 6 is properly classified as COMPILATION_ERROR with compile_output."""
    svc = Judge0ServiceClient(api_url="http://mock-judge0")
    svc.check_health = AsyncMock(return_value={"is_healthy": True, "status": "online"})

    mock_judge0_response = {
        "status": {"id": 6, "description": "Compilation Error"},
        "stdout": None,
        "stderr": None,
        "compile_output": "Main.java:5: error: ';' expected\n    int x = 10\n              ^",
        "time": "0.05",
        "memory": 12000,
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: mock_judge0_response
        mock_post.return_value = mock_resp

        result = await svc.execute_java_code("class Main {}", stdin_input="")
        assert not result["is_passed"]
        assert result["status"] == "Compilation Error"
        assert result["error_type"] == "COMPILATION_ERROR"
        assert "error: ';' expected" in result["compile_output"]


@pytest.mark.asyncio
async def test_judge0_client_runtime_error_classification():
    """Judge0 runtime error is classified as RUNTIME_ERROR with stderr."""
    svc = Judge0ServiceClient(api_url="http://mock-judge0")
    svc.check_health = AsyncMock(return_value={"is_healthy": True, "status": "online"})

    mock_judge0_response = {
        "status": {"id": 11, "description": "Runtime Error (NZEC)"},
        "stdout": "",
        "stderr": "Exception in thread \"main\" java.util.EmptyStackException\n\tat java.base/java.util.Stack.peek(Stack.java:102)",
        "compile_output": "",
        "time": "0.10",
        "memory": 24000,
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: mock_judge0_response
        mock_post.return_value = mock_resp

        result = await svc.execute_java_code("class Main {}", stdin_input="")
        assert not result["is_passed"]
        assert result["error_type"] == "RUNTIME_ERROR"
        assert "EmptyStackException" in result["stderr"]


# ==========================================
# 2. Valid Parentheses Exercise Tests
# ==========================================
def test_valid_parentheses_exercise_seed_data():
    """Verifies that the Valid Parentheses exercise contains all 5 required test cases."""
    db = SessionLocal()
    act = db.query(Activity).filter(Activity.slug == "valid-parentheses").first()
    assert act is not None
    assert "Valid Parentheses" in act.title

    test_cases = json.loads(act.test_cases_json)
    assert len(test_cases) == 5

    inputs_and_expected = {tc["input"]: tc["expected"] for tc in test_cases}
    assert inputs_and_expected["()"] == "true"
    assert inputs_and_expected["()[]{}"] == "true"
    assert inputs_and_expected["(]"] == "false"
    assert inputs_and_expected["([)]"] == "false"
    assert inputs_and_expected["{[]}"] == "true"

    db.close()


# ==========================================
# 3. Execution Routes Integration Tests
# ==========================================
def test_execution_run_endpoint_all_cases_passed_mock():
    """Simulates a correct Java solution passing all 5 test cases on /execution/run."""
    # Build mock returns for the 5 test cases:
    # 1: '()' -> true
    # 2: '()[]{}' -> true
    # 3: '(]' -> false
    # 4: '([)]' -> false
    # 5: '{[]}' -> true
    expected_outputs = ["true", "true", "false", "false", "true"]

    async def mock_execute(source_code, stdin_input, expected_output, **kwargs):
        return {
            "status": "Accepted",
            "is_passed": True,
            "stdout": expected_output + "\n",
            "stderr": "",
            "compile_output": "",
            "execution_time_ms": 15.0,
            "memory_kb": 12000.0,
            "is_service_available": True,
            "error_type": None,
        }

    with patch("app.routes.execution_routes.judge0_service.execute_java_code", side_effect=mock_execute):
        payload = {
            "learner_id": 1,
            "problem_id": 2,  # Valid Parentheses
            "code": "public class Main { public static void main(String[] args) {} }",
            "language": "java",
        }
        res = client.post("/api/v1/execution/run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        result = data["data"]
        assert result["status"] == "Accepted"
        assert result["is_passed"] is True
        assert result["test_cases_passed"] == 5
        assert result["total_test_cases"] == 5
        assert len(result["test_case_results"]) == 5


def test_execution_submit_persists_attempt_and_updates_bkt():
    """Submitting solution writes Attempt, CodeSubmission, ExecutionResult and updates BKT mastery."""
    async def mock_execute(source_code, stdin_input, expected_output, **kwargs):
        # Pass 4 out of 5 cases
        passed = (stdin_input != "([)]")
        return {
            "status": "Accepted" if passed else "Wrong Answer",
            "is_passed": passed,
            "stdout": expected_output + "\n" if passed else "true\n",
            "stderr": "",
            "compile_output": "",
            "execution_time_ms": 12.0,
            "memory_kb": 14000.0,
            "is_service_available": True,
            "error_type": None if passed else "WRONG_ANSWER",
        }

    with patch("app.routes.execution_routes.judge0_service.execute_java_code", side_effect=mock_execute):
        payload = {
            "learner_id": 1,
            "problem_id": 2,
            "code": "public class Main { public static boolean isValid(String s) { return true; } }",
            "language": "java",
        }
        res = client.post("/api/v1/execution/submit", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        result = data["data"]
        assert result["status"] == "Wrong Answer"
        assert result["test_cases_passed"] == 4
        assert result["total_test_cases"] == 5
        assert result["bkt_updated_mastery"] is not None

        # Verify DB records were persisted
        db = SessionLocal()
        attempt = (
            db.query(Attempt)
            .filter(Attempt.student_id == 1, Attempt.activity_id == 2)
            .order_by(Attempt.id.desc())
            .first()
        )
        assert attempt is not None
        assert not attempt.is_correct
        assert attempt.score == 80.0  # 4/5 = 80.0%

        code_sub = (
            db.query(CodeSubmission)
            .filter(CodeSubmission.attempt_id == attempt.id)
            .first()
        )
        assert code_sub is not None
        assert "isValid" in code_sub.source_code

        exec_res = db.query(ExecutionResult).filter(ExecutionResult.code_submission_id == code_sub.id).first()
        assert exec_res is not None
        assert exec_res.status == "Wrong Answer"
        assert exec_res.tests_passed == 4

        # Verify BKT skill state in DB
        act = db.query(Activity).filter(Activity.id == 2).first()
        skill_state = (
            db.query(LearnerSkillState)
            .filter(LearnerSkillState.student_id == 1, LearnerSkillState.topic_id == act.topic_id)
            .first()
        )
        assert skill_state is not None
        assert skill_state.total_attempts >= 1

        db.close()


def test_execution_history_endpoint():
    """GET /api/v1/execution/history/{student_id} returns student's logged submissions."""
    res = client.get("/api/v1/execution/history/1")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    first_item = data["data"][0]
    assert "status" in first_item
    assert "is_passed" in first_item
    assert "test_cases_passed" in first_item
