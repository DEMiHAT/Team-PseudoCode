"""
Curriculum and Concept/Topic routes for IT22301.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.topic import Topic
from app.models.unit import Unit
from app.models.activity import Activity
from app.models.learner_skill_state import LearnerSkillState
from app.schemas.concept import ConceptWithProblemCount
from app.utilities.response import ApiResponse, success_response

router = APIRouter()


@router.get("", response_model=ApiResponse[List[ConceptWithProblemCount]], summary="List all IT22301 topics")
def get_topics(
    learner_id: int = Query(default=1, description="Student ID to overlay current mastery status"),
    db: Session = Depends(get_db),
):
    """
    Returns list of all syllabus topics with activity count and student's current BKT mastery probability.
    """
    topics = db.query(Topic).join(Unit).order_by(Unit.unit_number, Topic.order_index).all()

    # Fetch learner knowledge states
    k_states = {
        ks.topic_id: ks.p_known
        for ks in db.query(LearnerSkillState).filter(LearnerSkillState.student_id == learner_id).all()
    }

    # Count activities per topic
    activity_counts = dict(
        db.query(Activity.topic_id, func.count(Activity.id))
        .filter(Activity.is_active == True)
        .group_by(Activity.topic_id)
        .all()
    )

    result = []
    for t in topics:
        unit_name = t.unit.title if t.unit else "General"
        result.append(
            ConceptWithProblemCount(
                id=t.id,
                code=t.code,
                name=t.name,
                category=unit_name,
                description=t.description,
                order_index=t.order_index,
                problem_count=activity_counts.get(t.id, 0),
                current_mastery_p=k_states.get(t.id, 0.20),
            )
        )

    return success_response(data=result, message=f"Retrieved {len(result)} curriculum topics")
