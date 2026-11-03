"""
Code Execution and Evaluation Routes.
Integrates Judge0 CE, cognitive misconception diagnosis, Attempt/Submission persistence,
and BKT LearnerSkillState updates.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.activity import Activity
from app.models.attempt import Attempt
from app.models.code_submission import CodeSubmission
from app.models.execution_result import ExecutionResult
from app.crud.crud_skill_state import learner_skill_state
from app.schemas.submission import (
    CodeSubmissionRequest,
    ExecutionResultResponse,
    TestCaseResult,
    SubmissionResponse,
)
from app.services.judge0_service import judge0_service
from app.intelligence.misconception_engine import MisconceptionEngine
from app.content.dsa_misconceptions import get_default_dsa_rules
from app.intelligence.intervention_selector import AdaptiveInterventionSelector
from app.intelligence.bkt import SkillType, BayesianKnowledgeTracer
from app.utilities.response import ApiResponse, success_response
from app.utilities.exceptions import ResourceNotFoundException

router = APIRouter()
diagnostic_engine = MisconceptionEngine(rules=get_default_dsa_rules())
bkt_tracer = BayesianKnowledgeTracer()


async def _evaluate_code_against_test_cases(
    code: str,
    raw_test_cases: List[Dict[str, Any]],
    only_public: bool = False,
) -> Dict[str, Any]:
    """Helper to evaluate code against test cases using Judge0."""
    test_case_results: List[TestCaseResult] = []
    passed_count = 0
    first_error = None
    all_passed = True
    total_time = 0.0
    status_str = "Accepted"
    compilation_error = None
    runtime_error = None

    cases_to_run = [tc for tc in raw_test_cases if not tc.get("is_hidden", False)] if only_public else raw_test_cases

    for tc in cases_to_run:
        exec_result = await judge0_service.execute_java_code(
            source_code=code,
            stdin_input=tc["input"],
            expected_output=tc["expected"],
        )

        tc_passed = exec_result.get("is_passed", False)
        err_type = exec_result.get("error_type")

        if exec_result.get("compile_output") and not compilation_error:
            compilation_error = exec_result.get("compile_output")
            status_str = "Compilation Error"
            first_error = compilation_error

        if exec_result.get("stderr") and not runtime_error:
            runtime_error = exec_result.get("stderr")
            if status_str != "Compilation Error":
                status_str = "Runtime Error"
                first_error = runtime_error

        if err_type == "TIME_LIMIT_EXCEEDED" and status_str not in ("Compilation Error", "Runtime Error"):
            status_str = "Time Limit Exceeded"
            first_error = "Execution timed out."

        if tc_passed:
            passed_count += 1
        else:
            all_passed = False
            if not first_error:
                first_error = f"Expected '{tc['expected']}' but got '{exec_result.get('stdout', '').strip()}'"
                if status_str not in ("Compilation Error", "Runtime Error", "Time Limit Exceeded"):
                    status_str = "Wrong Answer"

        total_time += exec_result.get("execution_time_ms", 0.0)

        # Do not expose hidden test case details
        if not tc.get("is_hidden", False) or only_public:
            test_case_results.append(
                TestCaseResult(
                    test_case_id=tc["id"],
                    passed=tc_passed,
                    input=tc["input"],
                    expected_output=tc["expected"],
                    actual_output=exec_result.get("stdout"),
                    error=exec_result.get("compile_output") or exec_result.get("stderr"),
                    execution_time_ms=exec_result.get("execution_time_ms"),
                )
            )

    if not all_passed and status_str == "Accepted":
        status_str = "Wrong Answer"

    return {
        "status_str": status_str,
        "all_passed": all_passed,
        "passed_count": passed_count,
        "total_cases": len(cases_to_run),
        "total_time": round(total_time, 2),
        "test_case_results": test_case_results,
        "first_error": first_error,
        "compile_error": compilation_error,
        "runtime_error": runtime_error,
    }


@router.post("/run", response_model=ApiResponse[ExecutionResultResponse], summary="Run code against sample test cases")
async def run_code(
    payload: CodeSubmissionRequest,
    db: Session = Depends(get_db),
):
    """
    Dry-run endpoint for testing student's Java code against visible test cases.
    Does not finalize or lock official assessment scores.
    """
    activity_obj = db.query(Activity).filter(Activity.id == payload.problem_id).first()
    if not activity_obj:
        raise ResourceNotFoundException("Activity", payload.problem_id)

    raw_test_cases = json.loads(activity_obj.test_cases_json or "[]")
    eval_data = await _evaluate_code_against_test_cases(
        code=payload.code,
        raw_test_cases=raw_test_cases,
        only_public=False,  # Run all test cases for direct feedback
    )

    response_payload = ExecutionResultResponse(
        status=eval_data["status_str"],
        is_passed=eval_data["all_passed"],
        test_cases_passed=eval_data["passed_count"],
        total_test_cases=eval_data["total_cases"],
        test_case_results=eval_data["test_case_results"],
        compile_error=eval_data["compile_error"],
        runtime_error=eval_data["runtime_error"],
        execution_time_ms=eval_data["total_time"],
        memory_kb=0.0,
        bkt_updated_mastery=None,
        triggered_intervention=None,
    )

    return success_response(
        data=response_payload,
        message=f"Test run completed: {eval_data['status_str']} ({eval_data['passed_count']}/{eval_data['total_cases']} passed)",
    )


@router.post("/submit", response_model=ApiResponse[ExecutionResultResponse], summary="Submit solution for assessment")
async def submit_code(
    payload: CodeSubmissionRequest,
    db: Session = Depends(get_db),
):
    """
    Submits code for official evaluation against full test suite.
    Persists Attempt, CodeSubmission, and ExecutionResult.
    Updates Bayesian Knowledge Tracing (BKT) skill states and diagnoses cognitive slips.
    """
    activity_obj = db.query(Activity).filter(Activity.id == payload.problem_id).first()
    if not activity_obj:
        raise ResourceNotFoundException("Activity", payload.problem_id)

    raw_test_cases = json.loads(activity_obj.test_cases_json or "[]")
    eval_data = await _evaluate_code_against_test_cases(
        code=payload.code,
        raw_test_cases=raw_test_cases,
        only_public=False,
    )

    all_passed = eval_data["all_passed"]
    status_str = eval_data["status_str"]
    passed_count = eval_data["passed_count"]

    # 1. Persist Attempt
    score = 100.0 if all_passed else ((passed_count / len(raw_test_cases) * 100.0) if raw_test_cases else 0.0)
    attempt_obj = Attempt(
        student_id=payload.learner_id,
        activity_id=payload.problem_id,
        is_correct=all_passed,
        score=round(score, 1),
        was_assisted=False,
        scaffolding_level_accessed=0,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    db.add(attempt_obj)
    db.flush()

    # 2. Persist CodeSubmission
    code_sub = CodeSubmission(
        attempt_id=attempt_obj.id,
        student_id=payload.learner_id,
        activity_id=payload.problem_id,
        source_code=payload.code,
        language=payload.language,
        submission_timestamp=datetime.now(timezone.utc),
    )
    db.add(code_sub)
    db.flush()

    # 3. Persist ExecutionResult
    exec_record = ExecutionResult(
        code_submission_id=code_sub.id,
        status=status_str,
        is_passed=all_passed,
        tests_passed=passed_count,
        total_tests=len(raw_test_cases),
        stdout="",
        stderr=eval_data["runtime_error"],
        compiler_output=eval_data["compile_error"],
        execution_time_ms=eval_data["total_time"],
        created_at=datetime.now(timezone.utc),
    )
    db.add(exec_record)

    # 4. Update Fine-Grained Cognitive Skill State (BKT Engine)
    updated_state = learner_skill_state.record_attempt_outcome(
        db,
        student_id=payload.learner_id,
        topic_id=activity_obj.topic_id,
        is_correct=all_passed,
        was_assisted=False,
        evidence_type="practical",
    )

    # 5. Diagnostic Misconception & Adaptive Intervention Selection
    misconceptions = []
    recommended_intervention = None

    if not all_passed:
        raw_diagnosed = diagnostic_engine.diagnose(
            code=payload.code,
            compiler_error=eval_data["compile_error"] or "",
            runtime_error=eval_data["runtime_error"] or "",
        )
        misconceptions = [m["name"] for m in raw_diagnosed]

        recommended_intervention = AdaptiveInterventionSelector.select_intervention(
            consecutive_failures=updated_state.consecutive_failures,
            p_known=updated_state.p_known,
            has_compilation_error="Compilation Error" in status_str,
            has_runtime_error="Error" in status_str,
            misconceptions=raw_diagnosed,
        )

    db.commit()

    response_payload = ExecutionResultResponse(
        status=status_str,
        is_passed=all_passed,
        test_cases_passed=passed_count,
        total_test_cases=len(raw_test_cases),
        test_case_results=eval_data["test_case_results"],
        compile_error=eval_data["compile_error"],
        runtime_error=eval_data["runtime_error"],
        execution_time_ms=eval_data["total_time"],
        memory_kb=0.0,
        bkt_updated_mastery=updated_state.p_known,
        triggered_intervention=recommended_intervention,
    )

    return success_response(
        data=response_payload,
        message=f"Solution submitted: {status_str} ({passed_count}/{len(raw_test_cases)} passed). Cognitive state updated.",
    )


@router.get("/history/{student_id}", response_model=ApiResponse[List[SubmissionResponse]], summary="Get student submission history")
def get_submission_history(student_id: int, db: Session = Depends(get_db)):
    """Retrieves all past code submissions and execution outcomes for a student."""
    submissions = (
        db.query(CodeSubmission)
        .filter(CodeSubmission.student_id == student_id)
        .order_by(CodeSubmission.submission_timestamp.desc())
        .limit(20)
        .all()
    )

    items = []
    for sub in submissions:
        exec_res = sub.execution_results[0] if sub.execution_results else None
        items.append(
            SubmissionResponse(
                id=sub.id,
                learner_id=sub.student_id,
                problem_id=sub.activity_id,
                status=exec_res.status if exec_res else "Pending",
                is_passed=exec_res.is_passed if exec_res else False,
                test_cases_passed=exec_res.tests_passed if exec_res else 0,
                total_test_cases=exec_res.total_tests if exec_res else 0,
                execution_time_ms=exec_res.execution_time_ms if exec_res else 0.0,
                created_at=sub.submission_timestamp,
            )
        )

    return success_response(data=items, message=f"Retrieved {len(items)} submission(s)")
