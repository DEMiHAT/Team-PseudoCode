"""
Learner profile and knowledge analytics routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.learner import Learner
from app.models.concept import Concept
from app.models.knowledge_state import KnowledgeState
from app.schemas.learner import (
    LearnerProfileResponse,
    LearnerResponse,
    ConceptMasterySummary,
)
from app.utilities.response import ApiResponse, success_response
from app.utilities.exceptions import ResourceNotFoundException

router = APIRouter()


@router.get("/{learner_id}/profile", response_model=ApiResponse[LearnerProfileResponse], summary="Get student mastery profile")
def get_learner_profile(learner_id: int, db: Session = Depends(get_db)):
    """
    Returns student profile along with BKT cognitive mastery values across all syllabus units.
    """
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise ResourceNotFoundException("Learner", learner_id)

    concepts = db.query(Concept).order_by(Concept.order_index).all()
    k_states = {
        ks.concept_id: ks
        for ks in db.query(KnowledgeState).filter(KnowledgeState.learner_id == learner_id).all()
    }

    overview = []
    total_mastery = 0.0

    for c in concepts:
        ks = k_states.get(c.id)
        p_val = ks.p_known if ks else 0.20
        total_mastery += p_val

        overview.append(
            ConceptMasterySummary(
                concept_id=c.id,
                concept_code=c.code,
                concept_name=c.name,
                category=c.category,
                p_known=round(p_val, 4),
                mastery_percentage=round(p_val * 100.0, 1),
                total_attempts=ks.total_attempts if ks else 0,
                successful_attempts=ks.successful_attempts if ks else 0,
            )
        )

    avg_mastery = round((total_mastery / len(concepts)) * 100.0, 1) if concepts else 0.0

    profile = LearnerProfileResponse(
        learner=LearnerResponse.model_validate(learner),
        mastery_overview=overview,
        overall_mastery_index=avg_mastery,
    )

    return success_response(data=profile, message="Learner mastery profile retrieved")
