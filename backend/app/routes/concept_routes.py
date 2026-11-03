"""
Curriculum and Concept routes for IT22301.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.concept import Concept
from app.models.problem import Problem
from app.models.knowledge_state import KnowledgeState
from app.schemas.concept import ConceptWithProblemCount
from app.utilities.response import ApiResponse, success_response

router = APIRouter()


@router.get("", response_model=ApiResponse[List[ConceptWithProblemCount]], summary="List all IT22301 concepts")
def get_concepts(
    learner_id: int = Query(default=1, description="Student ID to overlay current mastery status"),
    db: Session = Depends(get_db),
):
    """
    Returns list of all syllabus concepts with problem count and student's current BKT mastery probability.
    """
    concepts = db.query(Concept).order_index = db.query(Concept).order_by(Concept.order_index).all()

    # Fetch learner knowledge states
    k_states = {
        ks.concept_id: ks.p_known
        for ks in db.query(KnowledgeState).filter(KnowledgeState.learner_id == learner_id).all()
    }

    # Count problems per concept
    problem_counts = dict(
        db.query(Problem.concept_id, func.count(Problem.id))
        .filter(Problem.is_active == True)
        .group_by(Problem.concept_id)
        .all()
    )

    result = []
    for c in concepts:
        result.append(
            ConceptWithProblemCount(
                id=c.id,
                code=c.code,
                name=c.name,
                category=c.category,
                description=c.description,
                order_index=c.order_index,
                problem_count=problem_counts.get(c.id, 0),
                current_mastery_p=k_states.get(c.id, 0.20),
            )
        )

    return success_response(data=result, message=f"Retrieved {len(result)} curriculum concepts")
