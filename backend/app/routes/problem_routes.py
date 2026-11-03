"""
Problem browsing and problem workspace routes.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.problem import Problem
from app.models.concept import Concept
from app.schemas.problem import ProblemSummary, ProblemDetail, TestCaseItem
from app.utilities.response import ApiResponse, success_response
from app.utilities.exceptions import ResourceNotFoundException

router = APIRouter()


@router.get("", response_model=ApiResponse[List[ProblemSummary]], summary="List coding problems")
def list_problems(
    concept_id: Optional[int] = Query(default=None, description="Filter by concept ID"),
    db: Session = Depends(get_db),
):
    """Returns all active DSA practice problems, optionally filtered by concept."""
    query = db.query(Problem).filter(Problem.is_active == True)
    if concept_id:
        query = query.filter(Problem.concept_id == concept_id)

    problems = query.all()
    concept_ids = [p.concept_id for p in problems]
    concepts = {c.id: c.code for c in db.query(Concept).filter(Concept.id.in_(concept_ids)).all()}

    summaries = [
        ProblemSummary(
            id=p.id,
            concept_id=p.concept_id,
            concept_code=concepts.get(p.concept_id),
            title=p.title,
            slug=p.slug,
            difficulty=p.difficulty,
            is_active=p.is_active,
        )
        for p in problems
    ]

    return success_response(data=summaries, message=f"Retrieved {len(summaries)} problems")


@router.get("/{problem_id}", response_model=ApiResponse[ProblemDetail], summary="Get problem workspace details")
def get_problem_detail(problem_id: int, db: Session = Depends(get_db)):
    """Retrieves full problem details including Java starter code and visible test cases."""
    problem = db.query(Problem).filter(Problem.id == problem_id, Problem.is_active == True).first()
    if not problem:
        raise ResourceNotFoundException("Problem", problem_id)

    # Parse test cases and only expose public / non-hidden cases to the client
    raw_test_cases = json.loads(problem.test_cases_json)
    public_cases = [
        TestCaseItem(
            id=tc["id"],
            input=tc["input"],
            expected_output=tc["expected"],
            is_hidden=tc.get("is_hidden", False),
            explanation=tc.get("explanation"),
        )
        for tc in raw_test_cases
        if not tc.get("is_hidden", False)
    ]

    detail = ProblemDetail(
        id=problem.id,
        concept_id=problem.concept_id,
        title=problem.title,
        slug=problem.slug,
        difficulty=problem.difficulty,
        description_md=problem.description_md,
        starter_code_java=problem.starter_code_java,
        sample_test_cases=public_cases,
        is_active=problem.is_active,
    )

    return success_response(data=detail, message="Problem retrieved successfully")
