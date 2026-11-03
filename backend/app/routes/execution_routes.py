"""
Code execution and evaluation routes.
Integrates Judge0 CE, cognitive misconception diagnosis, and Bayesian Knowledge Tracing updates.
"""

import json
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.knowledge_state import KnowledgeState
from app.schemas.submission import (
    CodeSubmissionRequest,
    ExecutionResultResponse,
    TestCaseResult,
)
from app.services.judge0_service import judge0_service
from app.intelligence.bkt_engine import BKTEngine
from app.intelligence.misconception_engine import MisconceptionEngine
from app.intelligence.intervention_selector import AdaptiveInterventionSelector
from app.content.dsa_misconceptions import get_default_dsa_rules
from app.utilities.response import ApiResponse, success_response
from app.utilities.exceptions import ResourceNotFoundException

router = APIRouter()

# Instantiate diagnostic engine with IT22301 rules
diagnostic_engine = MisconceptionEngine(rules=get_default_dsa_rules())


@router.post("/run", response_model=ApiResponse[ExecutionResultResponse], summary="Run and evaluate Java code")
async def run_code(
    payload: CodeSubmissionRequest,
    db: Session = Depends(get_db),
):
    """
    Submits student's Java code to Judge0, evaluates against test cases,
    diagnoses misconceptions if failed, and updates the student's BKT cognitive state.
    """
    problem = db.query(Problem).filter(Problem.id == payload.problem_id).first()
    if not problem:
        raise ResourceNotFoundException("Problem", payload.problem_id)

    raw_test_cases = json.loads(problem.test_cases_json)
    test_case_results: List[TestCaseResult] = []
    passed_count = 0

    # Execute against each test case via Judge0
    first_error = None
    all_passed = True
    total_time = 0.0

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

        # Only reveal non-hidden test details in response
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

    # Save submission log to database
    submission = Submission(
        learner_id=payload.learner_id,
        problem_id=payload.problem_id,
        code=payload.code,
        language="java",
        status=status_str,
        execution_time_ms=total_time,
        memory_kb=0.0,
        is_passed=all_passed,
        test_cases_passed=passed_count,
        total_test_cases=len(raw_test_cases),
        output_log=first_error,
    )
    db.add(submission)

    # Update Bayesian Knowledge Tracing (BKT) State
    k_state = (
        db.query(KnowledgeState)
        .filter(
            KnowledgeState.learner_id == payload.learner_id,
            KnowledgeState.concept_id == problem.concept_id,
        )
        .first()
    )

    prior_p = k_state.p_known if k_state else 0.20
    bkt_result = BKTEngine.update_knowledge_state(
        prior_p_known=prior_p,
        is_correct=all_passed,
    )

    if k_state:
        k_state.p_known = bkt_result["next_prior_p_known"]
        k_state.total_attempts += 1
        if all_passed:
            k_state.successful_attempts += 1
        k_state.last_updated = datetime.now(timezone.utc)
    else:
        new_ks = KnowledgeState(
            learner_id=payload.learner_id,
            concept_id=problem.concept_id,
            p_known=bkt_result["next_prior_p_known"],
            total_attempts=1,
            successful_attempts=1 if all_passed else 0,
        )
        db.add(new_ks)

    # If failed, diagnose misconceptions and select intervention
    misconceptions = []
    recommended_intervention = None

    if not all_passed:
        misconceptions = diagnostic_engine.diagnose(
            code=payload.code,
            compiler_error=first_error or "",
            runtime_error="",
        )

        # Count consecutive failures by this student on this problem
        recent_failures = (
            db.query(Submission)
            .filter(
                Submission.learner_id == payload.learner_id,
                Submission.problem_id == payload.problem_id,
                Submission.is_passed == False,
            )
            .count()
        )

        recommended_intervention = AdaptiveInterventionSelector.select_intervention(
            consecutive_failures=recent_failures + 1,
            p_known=bkt_result["next_prior_p_known"],
            has_compilation_error="Compilation Error" in status_str,
            has_runtime_error="Error" in status_str,
            misconceptions=misconceptions,
        )

    db.commit()

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
        bkt_updated_mastery=bkt_result["next_prior_p_known"],
        triggered_intervention=recommended_intervention,
    )

    return success_response(
        data=response_payload,
        message="Code evaluation completed",
    )
