"""
Code execution and evaluation routes.
Integrates Judge0 CE, cognitive misconception diagnosis, and LearnerSkillState updates.
"""

import json
from typing import List
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
)
from app.services.judge0_service import judge0_service
from app.intelligence.misconception_engine import MisconceptionEngine
from app.intelligence.intervention_selector import AdaptiveInterventionSelector
from app.content.dsa_misconceptions import get_default_dsa_rules
from app.utilities.response import ApiResponse, success_response
from app.utilities.exceptions import ResourceNotFoundException

router = APIRouter()
diagnostic_engine = MisconceptionEngine(rules=get_default_dsa_rules())


@router.post("/run", response_model=ApiResponse[ExecutionResultResponse], summary="Run and evaluate Java code")
async def run_code(
    payload: CodeSubmissionRequest,
    db: Session = Depends(get_db),
):
    """
    Submits student's Java code to Judge0, evaluates against test vectors,
    diagnoses cognitive bugs if failed, records Attempt & CodeSubmission,
    and updates fine-grained LearnerSkillState evidence.
    """
    activity_obj = db.query(Activity).filter(Activity.id == payload.problem_id).first()
    if not activity_obj:
        raise ResourceNotFoundException("Activity", payload.problem_id)

    raw_test_cases = json.loads(activity_obj.test_cases_json or "[]")
    test_case_results: List[TestCaseResult] = []
    passed_count = 0
    first_error = None
    all_passed = True
    total_time = 0.0

    # 1. Execute against test suite
    for tc in raw_test_cases:
        exec_result = await judge0_service.execute_java_code(
            source_code=payload.code,
            stdin_input=tc["input"],
            expected_output=tc["expected"],
        )

        tc_passed = exec_result.get("is_passed", False)
        if tc_passed:
            passed_count += 1
        else:
            all_passed = False
            if not first_error:
                first_error = exec_result.get("compile_output") or exec_result.get("stderr") or "Output mismatch"

        total_time += exec_result.get("execution_time_ms", 0.0)

        if not tc.get("is_hidden", False):
            test_case_results.append(
                TestCaseResult(
                    test_case_id=tc["id"],
                    passed=tc_passed,
                    input=tc["input"],
                    expected_output=tc["expected"],
                    actual_output=exec_result.get("stdout"),
                    error=exec_result.get("stderr") or exec_result.get("compile_output"),
                    execution_time_ms=exec_result.get("execution_time_ms"),
                )
            )

    status_str = "Accepted" if (all_passed and len(raw_test_cases) > 0) else "Wrong Answer"
    if first_error and "compile" in first_error.lower():
        status_str = "Compilation Error"

    # 2. Persist Attempt
    attempt_obj = Attempt(
        student_id=payload.learner_id,
        activity_id=payload.problem_id,
        is_correct=all_passed,
        score=100.0 if all_passed else (passed_count / len(raw_test_cases) * 100.0 if raw_test_cases else 0.0),
        was_assisted=False,  # Can be flagged True if hints were queried during session
        scaffolding_level_accessed=0,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(attempt_obj)
    db.flush()

    # 3. Persist Practical Evidence: CodeSubmission & ExecutionResult
    code_sub = CodeSubmission(
        attempt_id=attempt_obj.id,
        student_id=payload.learner_id,
        activity_id=payload.problem_id,
        source_code=payload.code,
        language=payload.language,
    )
    db.add(code_sub)
    db.flush()

    exec_record = ExecutionResult(
        code_submission_id=code_sub.id,
        status=status_str,
        is_passed=all_passed,
        tests_passed=passed_count,
        total_tests=len(raw_test_cases),
        stdout="",
        stderr=first_error if "compile" not in status_str else None,
        compiler_output=first_error if "compile" in status_str else None,
        execution_time_ms=total_time,
    )
    db.add(exec_record)

    # 4. Update Fine-Grained Cognitive Skill State (Separating Practical Mastery & Tracking Independence)
    updated_state = learner_skill_state.record_attempt_outcome(
        db,
        student_id=payload.learner_id,
        topic_id=activity_obj.topic_id,
        is_correct=all_passed,
        was_assisted=False,
        evidence_type="practical",
    )

    # 5. Diagnostic Bug Evaluation & Intervention Recommendation
    misconceptions = []
    recommended_intervention = None

    if not all_passed:
        misconceptions = diagnostic_engine.diagnose(
            code=payload.code,
            compiler_error=first_error or "",
            runtime_error="",
        )

        recommended_intervention = AdaptiveInterventionSelector.select_intervention(
            consecutive_failures=updated_state.consecutive_failures,
            p_known=updated_state.p_known,
            has_compilation_error="Compilation Error" in status_str,
            has_runtime_error="Error" in status_str,
            misconceptions=misconceptions,
        )

    response_payload = ExecutionResultResponse(
        status=status_str,
        is_passed=all_passed,
        test_cases_passed=passed_count,
        total_test_cases=len(raw_test_cases),
        test_case_results=test_case_results,
        compile_error=first_error if "Compilation" in status_str else None,
        runtime_error=first_error if "Compilation" not in status_str and not all_passed else None,
        execution_time_ms=total_time,
        memory_kb=0.0,
        bkt_updated_mastery=updated_state.p_known,
        triggered_intervention=recommended_intervention,
    )

    return success_response(
        data=response_payload,
        message="Code evaluation and skill state update completed",
    )
