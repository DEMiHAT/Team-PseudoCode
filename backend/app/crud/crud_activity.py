"""
CRUD operations for Activity and Assessment entities.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.activity import Activity
from app.models.assessment import Assessment
from app.schemas.activity import ActivityCreate, ActivityBase
from app.schemas.assessment import AssessmentCreate, AssessmentBase


class CRUDActivity(CRUDBase[Activity, ActivityCreate, ActivityBase]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Activity]:
        return db.query(Activity).filter(Activity.slug == slug).first()

    def get_by_topic(self, db: Session, *, topic_id: int) -> List[Activity]:
        return db.query(Activity).filter(Activity.topic_id == topic_id, Activity.is_active == True).all()


class CRUDAssessment(CRUDBase[Assessment, AssessmentCreate, AssessmentBase]):
    def get_by_subject(self, db: Session, *, subject_id: int) -> List[Assessment]:
        return db.query(Assessment).filter(Assessment.subject_id == subject_id, Assessment.is_active == True).all()


activity = CRUDActivity(Activity)
assessment = CRUDAssessment(Assessment)
