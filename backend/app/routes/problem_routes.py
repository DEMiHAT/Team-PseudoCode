"""
Activity and Problem Workspace routes.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.activity import Activity
from app.models.topic import Topic
from app.schemas.problem import ProblemSummary, ProblemDetail, TestCaseItem
from app.utilities.response import ApiResponse, success_response
from app.utilities.exceptions import ResourceNotFoundException

router = APIRouter()


@router.get("", response_model=ApiResponse[List[ProblemSummary]], summary="List activities/problems")
def list_problems(
    concept_id: Optional[int] = Query(default=None, description="Filter by topic ID"),
    db: Session = Depends(get_db),
):
    """Returns active coding activities, optionally filtered by topic ID."""
    query = db.query(Activity).filter(Activity.is_active == True)
    if concept_id:
        query = query.filter(Activity.topic_id == concept_id)

    activities = query.all()
    topic_ids = [a.topic_id for a in activities]
    topics = {t.id: t.code for t in db.query(Topic).filter(Topic.id.in_(topic_ids)).all()}

    summaries = [
        ProblemSummary(
            id=a.id,
            concept_id=a.topic_id,
            concept_code=topics.get(a.topic_id),
            title=a.title,
            slug=a.slug,
            difficulty=a.difficulty,
            is_active=a.is_active,
        )
        for a in activities
    ]

    return success_response(data=summaries, message=f"Retrieved {len(summaries)} activities")


@router.get("/{problem_id}", response_model=ApiResponse[ProblemDetail], summary="Get problem workspace details")
def get_problem_detail(problem_id: int, db: Session = Depends(get_db)):
    """Retrieves full activity details including Java starter template and visible test cases."""
    activity_obj = db.query(Activity).filter(Activity.id == problem_id, Activity.is_active == True).first()
    if not activity_obj:
        raise ResourceNotFoundException("Activity", problem_id)

    raw_test_cases = json.loads(activity_obj.test_cases_json or "[]")
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
        id=activity_obj.id,
        concept_id=activity_obj.topic_id,
        title=activity_obj.title,
        slug=activity_obj.slug,
        difficulty=activity_obj.difficulty,
        description_md=activity_obj.description_md,
        starter_code_java=activity_obj.starter_template or "",
        sample_test_cases=public_cases,
        is_active=activity_obj.is_active,
    )

    return success_response(data=detail, message="Activity details retrieved successfully")
