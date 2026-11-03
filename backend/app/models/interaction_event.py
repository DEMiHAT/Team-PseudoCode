"""
Interaction Event database model.
Fine-grained telemetry and learner action logging.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class InteractionEvent(Base):
    """
    Granular user telemetry event (e.g., hint requested, editor run, code reset, tab switch).
    Allows fine-grained behavioral analysis and process mining.
    """

    __tablename__ = "interaction_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(60), nullable=False, index=True)  # 'editor_run_clicked', 'hint_expanded', 'tab_switched'
    entity_type = Column(String(50), nullable=True)  # 'activity', 'intervention', 'topic'
    entity_id = Column(Integer, nullable=True)
    event_payload = Column(Text, nullable=True)  # JSON-encoded payload
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    student = relationship("Student", back_populates="interaction_events")

    def __repr__(self):
        return f"<InteractionEvent id={self.id} student={self.student_id} type='{self.event_type}'>"

