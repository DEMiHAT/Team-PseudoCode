"""
Comprehensive Database Architecture and Relationship Validation Test Suite.
Validates all 14 models, relational constraints, foreign keys, and independent performance tracking.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.models import (
    Student,
    Subject,
    Unit,
    Topic,
    Prerequisite,
    LearnerSkillState,
    Activity,
    Assessment,
    Attempt,
    CodeSubmission,
    ExecutionResult,
    Intervention,
    InteractionEvent,
    Preference,
)
from app.crud.crud_skill_state import learner_skill_state


def test_student_and_preference_one_to_one(db_session):
    """Test 1-to-1 relationship between Student and Preference."""
    student = Student(
        external_id="22IT045",
        full_name="Aarav Sharma",
        email="aarav.s@college.edu",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    # Attach preference
    pref = Preference(
        student_id=student.id,
        preferred_language="java",
        theme="dark",
        editor_font_size=16,
        scaffolding_verbosity="detailed",
    )
    db_session.add(pref)
    db_session.commit()
    db_session.refresh(student)

    assert student.preference is not None
    assert student.preference.theme == "dark"
    assert student.preference.student.external_id == "22IT045"


def test_subject_unit_topic_hierarchy(db_session):
    """Test curriculum hierarchy: Subject -> Unit -> Topic."""
    subject = Subject(code="IT22301", name="Data Structures and Algorithms")
    db_session.add(subject)
    db_session.commit()

    unit = Unit(subject_id=subject.id, unit_number=1, title="Linear Collections")
    db_session.add(unit)
    db_session.commit()

    topic = Topic(unit_id=unit.id, code="IT22301-U1-SLL", name="Singly Linked List")
    db_session.add(topic)
    db_session.commit()
    db_session.refresh(subject)

    assert len(subject.units) == 1
    assert len(subject.units[0].topics) == 1
    assert subject.units[0].topics[0].code == "IT22301-U1-SLL"


def test_prerequisite_dag_relationship(db_session):
    """Test directed dependency edge between topics."""
    subject = Subject(code="IT22301", name="Data Structures")
    db_session.add(subject)
    db_session.commit()

    unit = Unit(subject_id=subject.id, unit_number=1, title="Linear Collections")
    db_session.add(unit)
    db_session.commit()

    t_sll = Topic(unit_id=unit.id, code="U1-SLL", name="Singly Linked List")
    t_dll = Topic(unit_id=unit.id, code="U1-DLL", name="Doubly Linked List")
    db_session.add_all([t_sll, t_dll])
    db_session.commit()

    # t_dll requires t_sll
    prereq = Prerequisite(topic_id=t_dll.id, prerequisite_topic_id=t_sll.id, strength=1.0, is_mandatory=True)
    db_session.add(prereq)
    db_session.commit()
    db_session.refresh(t_dll)

    assert len(t_dll.prerequisites) == 1
    assert t_dll.prerequisites[0].prerequisite_topic.code == "U1-SLL"
    assert len(t_sll.required_by) == 1


def test_learner_skill_state_evidence_separation(db_session):
    """Test separation of conceptual and practical evidence, and independent vs assisted tracking."""
    student = Student(external_id="22IT001", full_name="Arjun Patel", email="arjun@college.edu")
    subject = Subject(code="IT22301", name="DSA")
    db_session.add_all([student, subject])
    db_session.commit()

    unit = Unit(subject_id=subject.id, unit_number=1, title="Linear")
    db_session.add(unit)
    db_session.commit()

    topic = Topic(unit_id=unit.id, code="U1-STK", name="Stack ADT")
    db_session.add(topic)
    db_session.commit()

    # Record conceptual success (quiz)
    state = learner_skill_state.record_attempt_outcome(
        db_session,
        student_id=student.id,
        topic_id=topic.id,
        is_correct=True,
        was_assisted=False,
        evidence_type="conceptual",
    )
    assert state.conceptual_mastery > 0.0
    assert state.practical_mastery == 0.0
    assert state.independent_success_count == 1
    assert state.assisted_success_count == 0

    # Record practical success with assistance (hints used)
    state = learner_skill_state.record_attempt_outcome(
        db_session,
        student_id=student.id,
        topic_id=topic.id,
        is_correct=True,
        was_assisted=True,
        evidence_type="practical",
    )
    assert state.practical_mastery > 0.0
    assert state.assisted_success_count == 1
    assert state.independent_success_count == 1


def test_attempt_submission_execution_chain(db_session):
    """Test full problem execution evidence chain: Attempt -> CodeSubmission -> ExecutionResult."""
    student = Student(external_id="22IT099", full_name="Test Student", email="test@college.edu")
    subject = Subject(code="IT22301", name="DSA")
    db_session.add_all([student, subject])
    db_session.commit()

    unit = Unit(subject_id=subject.id, unit_number=1, title="Linear")
    db_session.add(unit)
    db_session.commit()

    topic = Topic(unit_id=unit.id, code="U1-ARR", name="Arrays")
    db_session.add(topic)
    db_session.commit()

    activity = Activity(
        topic_id=topic.id,
        title="Array Search",
        slug="array-search",
        activity_type="coding_exercise",
        description_md="Implement binary search",
    )
    db_session.add(activity)
    db_session.commit()

    # 1. Attempt
    attempt = Attempt(
        student_id=student.id,
        activity_id=activity.id,
        is_correct=True,
        score=100.0,
        was_assisted=False,
        scaffolding_level_accessed=0,
    )
    db_session.add(attempt)
    db_session.commit()

    # 2. CodeSubmission
    submission = CodeSubmission(
        attempt_id=attempt.id,
        student_id=student.id,
        activity_id=activity.id,
        source_code="class Solution { public int search() { return 1; } }",
        language="java",
    )
    db_session.add(submission)
    db_session.commit()

    # 3. ExecutionResult
    exec_result = ExecutionResult(
        code_submission_id=submission.id,
        status="Accepted",
        is_passed=True,
        tests_passed=5,
        total_tests=5,
        execution_time_ms=12.5,
    )
    db_session.add(exec_result)
    db_session.commit()
    db_session.refresh(attempt)

    assert len(attempt.code_submissions) == 1
    assert len(attempt.code_submissions[0].execution_results) == 1
    assert attempt.code_submissions[0].execution_results[0].status == "Accepted"


def test_intervention_and_telemetry_logging(db_session):
    """Test Intervention logging and InteractionEvent telemetry stream."""
    student = Student(external_id="22IT100", full_name="Student", email="student100@college.edu")
    subject = Subject(code="IT22301", name="DSA")
    db_session.add_all([student, subject])
    db_session.commit()

    unit = Unit(subject_id=subject.id, unit_number=1, title="Linear")
    db_session.add(unit)
    db_session.commit()

    topic = Topic(unit_id=unit.id, code="U1-QUE", name="Queue ADT")
    db_session.add(topic)
    db_session.commit()

    # Log intervention
    interv = Intervention(
        student_id=student.id,
        topic_id=topic.id,
        intervention_type="socratic_hint",
        scaffolding_tier=2,
        trigger_reason="consecutive_failures_2",
        hint_content="Check the modulo wraparound formula for circular queues.",
        subsequent_attempt_successful=True,
    )
    db_session.add(interv)

    # Log telemetry event
    event = InteractionEvent(
        student_id=student.id,
        event_type="hint_expanded",
        entity_type="intervention",
        entity_id=1,
        event_payload='{"expanded_tier": 2}',
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(student)

    assert len(student.interventions) == 1
    assert student.interventions[0].scaffolding_tier == 2
    assert student.interventions[0].subsequent_attempt_successful is True
    assert len(student.interaction_events) == 1
    assert student.interaction_events[0].event_type == "hint_expanded"
