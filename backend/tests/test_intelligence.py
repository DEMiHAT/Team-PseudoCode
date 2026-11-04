from app.models import Attempt, Diagnosis, Intervention, Mastery, Problem, Student
from app.services.diagnosis import diagnose
from app.services.interventions import select_intervention

def test_diagnoses_compiler_signal(db):
    p=db.query(Problem).first(); a=Attempt(student_id=1,problem_id=p.id,source_code='bad code here',status='COMPLETED',correct=False,compiler_output="error: ';' expected",results=[])
    result=diagnose(a,p); assert result['category']=='Compilation error'; assert result['confidence']>.9

def test_policy_recommends_independent_work_for_high_mastery(db):
    s=Student(name='Grace',email='grace@example.com'); db.add(s); db.flush(); p=db.query(Problem).first(); db.add(Mastery(student_id=s.id,concept_id=p.concept_id,probability=.9)); db.commit()
    result=select_intervention(db,s.id,p.concept_id); assert result['scaffold_level']==0; assert result['kind']=='Independent practice'
