"""
CRUD operations for Intervention entity.
Maintains intervention history and tracks pedagogical efficacy.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.intervention import Intervention
from app.schemas.intervention import InterventionCreate, InterventionBase


class CRUDIntervention(CRUDBase[Intervention, InterventionCreate, InterventionBase]):
    def get_by_student_and_topic(
        self, db: Session, *, student_id: int, topic_id: int
    ) -> List[Intervention]:
        return (
            db.query(Intervention)
            .filter(
                Intervention.student_id == student_id,
                Intervention.topic_id == topic_id,
            )
            .order_by(Intervention.created_at.desc())
            .all()
        )

    def record_efficacy(
        self, db: Session, *, intervention_id: int, was_successful: bool
    ) -> Optional[Intervention]:
        """Updates whether the intervention yielded independent success."""
        intervention_obj = self.get(db, id=intervention_id)
        if intervention_obj:
            intervention_obj.subsequent_attempt_successful = was_successful
            db.commit()
            db.refresh(intervention_obj)
        return intervention_obj


intervention = CRUDIntervention(Intervention)

