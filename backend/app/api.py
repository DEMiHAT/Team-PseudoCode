from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.models import Assessment, AssessmentResult, Attempt, Concept, Course, Diagnosis, Intervention, LearningEvent, Mastery, MasteryHistory, Problem, Student
from app.schemas import AssessmentSubmit, AttemptOut, ConceptDetail, ConceptOut, CourseOut, DiagnosisRequest, EventCreate, InterventionRequest, MasteryOut, ProblemOut, StudentCreate, StudentOut, SubmissionCreate, TutorRequest
from app.services.bkt import update
from app.services.diagnosis import diagnose
from app.services.interventions import select_intervention
from app.services.judge0 import Judge0Service, JudgeUnavailable
from app.services.tutor import tutor_response

router = APIRouter(prefix="/api/v1")

def need(db, cls, ident):
    obj = db.get(cls, ident)
    if not obj: raise HTTPException(404, f"{cls.__name__} not found")
    return obj

@router.post("/students", response_model=StudentOut, status_code=201)
def create_student(body: StudentCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Student).where(Student.email == body.email))
    if existing: return existing
    student = Student(**body.model_dump()); db.add(student); db.flush()
    for concept_id in db.scalars(select(Concept.id)):
        db.add(Mastery(student_id=student.id, concept_id=concept_id, probability=.2))
    db.commit(); db.refresh(student); return student

@router.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)): return need(db, Student, student_id)

@router.get("/students/{student_id}/profile")
def profile(student_id: int, db: Session = Depends(get_db)):
    student = need(db, Student, student_id)
    return {"student": StudentOut.model_validate(student), "attempts": db.scalar(select(func.count()).select_from(Attempt).where(Attempt.student_id == student_id)), "events": db.scalar(select(func.count()).select_from(LearningEvent).where(LearningEvent.student_id == student_id))}

@router.get("/courses", response_model=list[CourseOut])
def courses(db: Session = Depends(get_db)): return db.scalars(select(Course)).all()

@router.get("/courses/{course_id}/concepts", response_model=list[ConceptOut])
def concepts(course_id: int, db: Session = Depends(get_db)):
    need(db, Course, course_id); return db.scalars(select(Concept).where(Concept.course_id == course_id).order_by(Concept.position)).all()

@router.get("/concepts/{concept_id}", response_model=ConceptDetail)
def concept(concept_id: int, db: Session = Depends(get_db)): return need(db, Concept, concept_id)

@router.get("/concepts/{concept_id}/lesson", response_model=ConceptDetail)
def lesson(concept_id: int, student_id: int | None = None, db: Session = Depends(get_db)):
    item = need(db, Concept, concept_id)
    if student_id:
        need(db, Student, student_id); db.add(LearningEvent(student_id=student_id, concept_id=concept_id, kind="lesson_opened")); db.commit()
    return item

@router.get("/problems", response_model=list[ProblemOut])
def problems(concept_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Problem)
    if concept_id: query = query.where(Problem.concept_id == concept_id)
    return db.scalars(query).all()

@router.get("/students/{student_id}/mastery", response_model=list[MasteryOut])
def mastery(student_id: int, db: Session = Depends(get_db)):
    need(db, Student, student_id); return db.scalars(select(Mastery).where(Mastery.student_id == student_id)).all()

@router.get("/concepts/{concept_id}/mastery")
def concept_mastery(concept_id: int, student_id: int = Query(...), db: Session = Depends(get_db)):
    item = db.scalar(select(Mastery).where(Mastery.student_id == student_id, Mastery.concept_id == concept_id))
    if not item: raise HTTPException(404, "Mastery estimate not found")
    return {"concept_id": concept_id, "student_id": student_id, "estimate": item.probability, "observations": item.observations}

@router.get("/students/{student_id}/dashboard")
def dashboard(student_id: int, db: Session = Depends(get_db)):
    need(db, Student, student_id)
    rows = db.execute(select(Mastery, Concept).join(Concept, Concept.id == Mastery.concept_id).where(Mastery.student_id == student_id)).all()
    concepts = [{"id": c.id, "title": c.title, "probability": m.probability, "observations": m.observations} for m, c in rows]
    attempts = db.scalars(select(Attempt).where(Attempt.student_id == student_id).order_by(Attempt.id.desc()).limit(8)).all()
    evaluated = [a for a in attempts if a.correct is not None]
    return {"mastery": concepts, "overall": sum(x["probability"] for x in concepts) / max(len(concepts), 1), "accuracy": sum(bool(a.correct) for a in evaluated) / max(len(evaluated), 1), "recent_attempts": [AttemptOut.model_validate(a) for a in attempts], "recommended_next": min(concepts, key=lambda x: x["probability"]) if concepts else None}

@router.post("/events", status_code=201)
def event(body: EventCreate, db: Session = Depends(get_db)):
    need(db, Student, body.student_id); item = LearningEvent(**body.model_dump()); db.add(item); db.commit(); return {"id": item.id}

@router.post("/submissions", response_model=AttemptOut, status_code=202)
def submit(body: SubmissionCreate, tasks: BackgroundTasks, db: Session = Depends(get_db)):
    need(db, Student, body.student_id); need(db, Problem, body.problem_id)
    attempt = Attempt(**body.model_dump(), status="QUEUED"); db.add(attempt); db.add(LearningEvent(student_id=body.student_id, kind="code_submitted", payload={"problem_id": body.problem_id})); db.commit(); db.refresh(attempt)
    tasks.add_task(evaluate_attempt, attempt.id); return attempt

async def evaluate_attempt(attempt_id: int):
    with SessionLocal() as db:
        attempt = need(db, Attempt, attempt_id); problem = need(db, Problem, attempt.problem_id); attempt.status = "RUNNING"; db.commit()
        try:
            result = await Judge0Service().evaluate(attempt.source_code, problem.visible_cases + problem.hidden_cases)
            attempt.status = "EVALUATED"; attempt.correct = result["correct"]; attempt.compiler_output = result["compiler_output"]; attempt.runtime_ms = result["runtime_ms"]; attempt.memory_kb = result["memory_kb"]
            attempt.results = [{k: v for k, v in r.items() if k != "input" or v is not None} for r in result["results"]]; db.flush()
            mastery_row = db.scalar(select(Mastery).where(Mastery.student_id == attempt.student_id, Mastery.concept_id == problem.concept_id))
            before = mastery_row.probability; after = update(before, bool(attempt.correct)); mastery_row.probability = after; mastery_row.observations += 1
            db.add(MasteryHistory(mastery_id=mastery_row.id, attempt_id=attempt.id, before=before, after=after, correct=bool(attempt.correct)))
            diagnosis_row = None
            if not attempt.correct:
                d = diagnose(attempt, problem); diagnosis_row = Diagnosis(attempt_id=attempt.id, concept_id=problem.concept_id, **d); db.add(diagnosis_row); db.flush()
            policy = select_intervention(db, attempt.student_id, problem.concept_id, diagnosis_row)
            db.add(Intervention(student_id=attempt.student_id, concept_id=problem.concept_id, diagnosis_id=diagnosis_row.id if diagnosis_row else None, **policy))
            db.add(LearningEvent(student_id=attempt.student_id, concept_id=problem.concept_id, kind="submission_evaluated", payload={"attempt_id": attempt.id, "correct": attempt.correct, "mastery_before": before, "mastery_after": after})); attempt.status = "COMPLETED"; db.commit()
        except JudgeUnavailable as exc:
            attempt.status = "FAILED"; attempt.compiler_output = str(exc); db.commit()

@router.get("/submissions/{attempt_id}", response_model=AttemptOut)
def submission(attempt_id: int, db: Session = Depends(get_db)): return need(db, Attempt, attempt_id)

@router.post("/diagnosis")
def diagnosis(body: DiagnosisRequest, db: Session = Depends(get_db)):
    attempt = need(db, Attempt, body.attempt_id)
    existing = db.scalar(select(Diagnosis).where(Diagnosis.attempt_id == attempt.id))
    if existing: return existing
    if attempt.correct is None: raise HTTPException(409, "Attempt has not been evaluated")
    problem = need(db, Problem, attempt.problem_id); row = Diagnosis(attempt_id=attempt.id, concept_id=problem.concept_id, **diagnose(attempt, problem)); db.add(row); db.commit(); db.refresh(row); return row

@router.post("/interventions/next")
def intervention(body: InterventionRequest, db: Session = Depends(get_db)):
    diagnosis_row = need(db, Diagnosis, body.diagnosis_id) if body.diagnosis_id else None
    policy = select_intervention(db, body.student_id, body.concept_id, diagnosis_row); row = Intervention(student_id=body.student_id, concept_id=body.concept_id, diagnosis_id=body.diagnosis_id, **policy); db.add(row); db.commit(); db.refresh(row); return row

@router.get("/students/{student_id}/learning-history")
def history(student_id: int, db: Session = Depends(get_db)):
    need(db, Student, student_id); return db.scalars(select(LearningEvent).where(LearningEvent.student_id == student_id).order_by(LearningEvent.id.desc()).limit(100)).all()

async def _tutor(body: TutorRequest, db: Session):
    concept = need(db, Concept, body.concept_id)
    mastery_row = db.scalar(select(Mastery).where(Mastery.student_id == body.student_id, Mastery.concept_id == body.concept_id))
    intervention_row = need(db, Intervention, body.intervention_id) if body.intervention_id else db.scalar(select(Intervention).where(Intervention.student_id == body.student_id, Intervention.concept_id == body.concept_id).order_by(Intervention.id.desc()))
    diagnosis_row = db.get(Diagnosis, intervention_row.diagnosis_id) if intervention_row and intervention_row.diagnosis_id else None
    context = {"concept": concept.title, "mastery_estimate": round(mastery_row.probability, 3) if mastery_row else .2, "diagnosis": diagnosis_row.category if diagnosis_row else "none", "intervention": intervention_row.kind if intervention_row else "conceptual hint", "scaffold_level": intervention_row.scaffold_level if intervention_row else 1, "student_question": body.question or "Provide the next helpful prompt."}
    text, fallback = await tutor_response(context); db.add(LearningEvent(student_id=body.student_id, concept_id=body.concept_id, kind="hint_viewed", payload={"fallback": fallback, "scaffold_level": context["scaffold_level"]})); db.commit()
    return {"response": text, "fallback": fallback, "context": context}

@router.post("/tutor/hints")
async def hint(body: TutorRequest, db: Session = Depends(get_db)): return await _tutor(body, db)
@router.post("/tutor/explanations")
async def explanation(body: TutorRequest, db: Session = Depends(get_db)): return await _tutor(body, db)
@router.post("/tutor/questions")
async def question(body: TutorRequest, db: Session = Depends(get_db)): return await _tutor(body, db)

@router.get("/assessments")
def assessments(db: Session = Depends(get_db)): return db.scalars(select(Assessment)).all()

@router.post("/assessments/{assessment_id}/submit")
def submit_assessment(assessment_id: int, body: AssessmentSubmit, db: Session = Depends(get_db)):
    assessment = need(db, Assessment, assessment_id); attempts = db.scalars(select(Attempt).where(Attempt.id.in_(body.attempt_ids), Attempt.student_id == body.student_id, Attempt.assisted.is_(False), Attempt.status == "COMPLETED")).all()
    allowed = set(assessment.problem_ids); valid = [a for a in attempts if a.problem_id in allowed]
    if not valid: raise HTTPException(422, "No completed independent attempts supplied")
    performance = {}; correct = 0
    for attempt in valid:
        problem = need(db, Problem, attempt.problem_id); performance.setdefault(str(problem.concept_id), {"correct": 0, "total": 0}); performance[str(problem.concept_id)]["total"] += 1
        if attempt.correct: performance[str(problem.concept_id)]["correct"] += 1; correct += 1
    row = AssessmentResult(assessment_id=assessment_id, student_id=body.student_id, score=100 * correct / len(valid), concept_performance=performance); db.add(row); db.add(LearningEvent(student_id=body.student_id, kind="assessment_completed", payload={"assessment_id": assessment_id, "score": row.score})); db.commit(); return row
