"""
CRUD operations for InteractionEvent entity.
"""

from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.interaction_event import InteractionEvent
from app.schemas.interaction_event import InteractionEventCreate


class CRUDInteractionEvent(CRUDBase[InteractionEvent, InteractionEventCreate, InteractionEventCreate]):
    def get_by_student(
        self, db: Session, *, student_id: int, limit: int = 100
    ) -> List[InteractionEvent]:
        return (
            db.query(InteractionEvent)
            .filter(InteractionEvent.student_id == student_id)
            .order_by(InteractionEvent.timestamp.desc())
            .limit(limit)
            .all()
        )


interaction_event = CRUDInteractionEvent(InteractionEvent)

