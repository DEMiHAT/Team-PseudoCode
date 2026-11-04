from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Attempt, Diagnosis, Intervention, Mastery

def select_intervention(db: Session, student_id: int, concept_id: int, diagnosis: Diagnosis | None = None) -> dict:
    mastery = db.scalar(select(Mastery).where(Mastery.student_id == student_id, Mastery.concept_id == concept_id))
    probability = mastery.probability if mastery else .2
    attempts = len(db.scalars(select(Attempt).where(Attempt.student_id == student_id)).all())
    previous = db.scalars(select(Intervention).where(Intervention.student_id == student_id, Intervention.concept_id == concept_id).order_by(Intervention.id.desc()).limit(3)).all()
    category = diagnosis.category if diagnosis else ""
    if probability >= .8: level, kind = 0, "Independent practice"
    elif category == "Boundary condition error": level, kind = 3, "Guided trace"
    elif category in {"Compilation error", "Syntax error"}: level, kind = 2, "Conceptual explanation"
    elif attempts >= 4 and probability < .35: level, kind = 5, "Detailed walkthrough"
    elif probability < .4: level, kind = 4, "Partial algorithm guidance"
    elif probability < .65: level, kind = 2, "Visual reinforcement"
    else: level, kind = 1, "Targeted conceptual question"
    used = {p.kind for p in previous}
    if kind in used and level not in {0, 5}:
        kind = "Guided trace" if kind != "Guided trace" else "Targeted conceptual question"
    return {"kind": kind, "scaffold_level": level, "rationale": f"Mastery estimate {probability:.0%}; {category or 'no active diagnosis'}; {attempts} total attempt(s)."}
