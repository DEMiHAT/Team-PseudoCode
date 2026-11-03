"""
Student profile and cognitive mastery analytics routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.student import Student
from app.models.topic import Topic
from app.models.unit import Unit
from app.models.learner_skill_state import LearnerSkillState
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
    Avoids collapsing mastery into a single score.
    """
    student_obj = db.query(Student).filter(Student.id == learner_id).first()
    if not student_obj:
        # Create a candidate record if none exists yet
        student_obj = Student(
            external_id=f"22IT00{learner_id}",
            full_name="Enrolled Candidate",
            email=f"candidate{learner_id}@engineering.edu",
            is_active=True,
        )
        db.add(student_obj)
        db.commit()
        db.refresh(student_obj)

    topics = db.query(Topic).join(Unit).order_by(Unit.unit_number, Topic.order_index).all()
    k_states = {
        ks.topic_id: ks
        for ks in db.query(LearnerSkillState).filter(LearnerSkillState.student_id == student_obj.id).all()
    }

    overview = []
    total_mastery = 0.0

    for t in topics:
        ks = k_states.get(t.id)
        p_val = ks.p_known if ks else 0.20
        total_mastery += p_val

        overview.append(
            ConceptMasterySummary(
                concept_id=t.id,
                concept_code=t.code,
                concept_name=t.name,
                category=t.unit.title if t.unit else "General",
                p_known=round(p_val, 4),
                mastery_percentage=round(p_val * 100.0, 1),
                total_attempts=ks.total_attempts if ks else 0,
                successful_attempts=(ks.independent_success_count + ks.assisted_success_count) if ks else 0,
            )
        )

    avg_mastery = round((total_mastery / len(topics)) * 100.0, 1) if topics else 0.0

    profile = LearnerProfileResponse(
        learner=LearnerResponse(
            id=student_obj.id,
            student_id=student_obj.external_id,
            full_name=student_obj.full_name,
            email=student_obj.email,
            semester=3,
            created_at=student_obj.created_at,
        ),
        mastery_overview=overview,
        overall_mastery_index=avg_mastery,
    )

    return success_response(data=profile, message="Learner mastery profile retrieved")
