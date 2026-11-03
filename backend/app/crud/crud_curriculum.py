"""
CRUD operations for Subject, Unit, Topic, and Prerequisite entities.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.subject import Subject
from app.models.unit import Unit
from app.models.topic import Topic
from app.models.prerequisite import Prerequisite
from app.schemas.subject import SubjectCreate, SubjectBase
from app.schemas.unit import UnitCreate, UnitBase
from app.schemas.topic import TopicCreate, TopicBase
from app.schemas.prerequisite import PrerequisiteCreate, PrerequisiteBase


class CRUDSubject(CRUDBase[Subject, SubjectCreate, SubjectBase]):
    def get_by_code(self, db: Session, *, code: str) -> Optional[Subject]:
        return db.query(Subject).filter(Subject.code == code).first()


class CRUDUnit(CRUDBase[Unit, UnitCreate, UnitBase]):
    def get_by_subject(self, db: Session, *, subject_id: int) -> List[Unit]:
        return db.query(Unit).filter(Unit.subject_id == subject_id).order_by(Unit.unit_number).all()


class CRUDTopic(CRUDBase[Topic, TopicCreate, TopicBase]):
    def get_by_code(self, db: Session, *, code: str) -> Optional[Topic]:
        return db.query(Topic).filter(Topic.code == code).first()

    def get_by_unit(self, db: Session, *, unit_id: int) -> List[Topic]:
        return db.query(Topic).filter(Topic.unit_id == unit_id).order_by(Topic.order_index).all()


class CRUDPrerequisite(CRUDBase[Prerequisite, PrerequisiteCreate, PrerequisiteBase]):
    def get_prerequisites_for_topic(self, db: Session, *, topic_id: int) -> List[Prerequisite]:
        return db.query(Prerequisite).filter(Prerequisite.topic_id == topic_id).all()


subject = CRUDSubject(Subject)
unit = CRUDUnit(Unit)
topic = CRUDTopic(Topic)
prerequisite = CRUDPrerequisite(Prerequisite)
