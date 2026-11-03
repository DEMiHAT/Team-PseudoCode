"""
CRUD operations for Student and Preference entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.student import Student
from app.models.preference import Preference
from app.schemas.student import StudentCreate, StudentUpdate
from app.schemas.preference import PreferenceCreate, PreferenceUpdate


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def get_by_external_id(self, db: Session, *, external_id: str) -> Optional[Student]:
        return db.query(Student).filter(Student.external_id == external_id).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Student]:
        return db.query(Student).filter(Student.email == email).first()

    def create_with_default_preferences(
        self, db: Session, *, student_in: StudentCreate
    ) -> Student:
        student = self.create(db, obj_in=student_in)
        # Automatically generate default preference record
        pref = Preference(student_id=student.id)
        db.add(pref)
        db.commit()
        db.refresh(student)
        return student


class CRUDPreference(CRUDBase[Preference, PreferenceCreate, PreferenceUpdate]):
    def get_by_student_id(self, db: Session, *, student_id: int) -> Optional[Preference]:
        return db.query(Preference).filter(Preference.student_id == student_id).first()


student = CRUDStudent(Student)
preference = CRUDPreference(Preference)

