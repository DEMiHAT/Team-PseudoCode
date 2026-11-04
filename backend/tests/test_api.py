from app.api import courses, concepts, create_student, dashboard, mastery, problems
from app.schemas import StudentCreate

def test_curriculum_and_student_flow(db):
    course=courses(db)[0]
    concept_rows=concepts(course.id,db); assert len(concept_rows)==11
    student=create_student(StudentCreate(name='Ada Lovelace',email='ada@example.com'),db)
    mastery_rows=mastery(student.id,db); assert len(mastery_rows)==11
    dashboard_data=dashboard(student.id,db); assert dashboard_data['overall']==.2

def test_hidden_cases_excluded_by_public_response_schema(db):
    from app.schemas import ProblemOut
    problem=ProblemOut.model_validate(problems(None,db)[0]).model_dump()
    assert 'hidden_cases' not in problem
    assert 'expected' in problem['visible_cases'][0]
