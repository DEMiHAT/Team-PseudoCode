"""
Preference database model.
Maintains student UI, editor, and accessibility configurations.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Preference(Base):
    """
    1-to-1 student preference profile.
    Controls IDE themes, language selection, and cognitive scaffolding verbosity.
    """

    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    preferred_language = Column(String(30), default="java", nullable=False)
    theme = Column(String(20), default="dark", nullable=False)  # 'dark', 'light'
    editor_font_size = Column(Integer, default=14, nullable=False)
    scaffolding_verbosity = Column(String(20), default="balanced", nullable=False)  # 'minimal', 'balanced', 'detailed'
    audio_explanations_enabled = Column(Boolean, default=False, nullable=False)

    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="preference")

    def __repr__(self):
        return f"<Preference id={self.id} student={self.student_id} lang='{self.preferred_language}'>"

