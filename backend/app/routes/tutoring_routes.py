"""
Adaptive Tutoring and AI Scaffolding Routes.
Integrates the Gemini AI Tutoring infrastructure with progressive scaffolding and misconception diagnosis.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.activity import Activity
from app.models.intervention import Intervention
from app.schemas.intelligence import (
    ScaffoldingRequest,
    ScaffoldingHintResponse,
    DiagnosisRequest,
    DiagnosisResponse,
    MisconceptionItem,
)
from app.ai_tutor import (
    tutor_orchestrator,
    HintRequest,
    ErrorExplanationRequest,
    ConceptSimplificationRequest,
    PracticeQuestionRequest,
    TutorResponse,
    PracticeQuestionResponse,
)
from app.intelligence.scaffolding import ProgressiveScaffoldingEngine
from app.intelligence.misconception_engine import MisconceptionEngine
from app.content.dsa_misconceptions import get_default_dsa_rules
from app.utilities.response import ApiResponse, success_response
from app.utilities.exceptions import ResourceNotFoundException

router = APIRouter()
diagnostic_engine = MisconceptionEngine(rules=get_default_dsa_rules())


# ==========================================
# 1. AI Tutor Health Endpoint
# ==========================================
@router.get("/health", response_model=ApiResponse[Dict[str, Any]], summary="AI Tutoring subsystem status")
async def get_ai_tutor_health():
    """Returns the operational status of the Gemini API and AI Tutoring subsystem."""
    health_data = await tutor_orchestrator.get_health_status()
    return success_response(data=health_data, message="AI Tutor health retrieved")


# ==========================================
# 2. Socratic Hint Generation Interface
# ==========================================
@router.post("/hint", response_model=ApiResponse[TutorResponse], summary="Generate scaffold-aligned Socratic hint")
async def request_socratic_hint(
    payload: HintRequest,
    db: Session = Depends(get_db),
):
    """
    Generates a single actionable hint aligned with the student's scaffold level (L1-L5).
    Falls back to deterministic scaffolding if Gemini API is unconfigured or unreachable.
    """
    response = await tutor_orchestrator.provide_scaffolded_hint(request=payload, db=db)
    return success_response(
        data=response,
        message=f"Level {response.scaffold_level} hint generated {'(Fallback)' if response.is_fallback else '(AI)'}",
    )


# ==========================================
# 3. Code Error Explanation Interface
# ==========================================
@router.post("/explain-error", response_model=ApiResponse[TutorResponse], summary="Explain code compiler/runtime error")
async def explain_code_error(
    payload: ErrorExplanationRequest,
    db: Session = Depends(get_db),
):
    """
    Explains verified execution errors and exceptions without inventing hallucinations.
    """
    response = await tutor_orchestrator.explain_code_error(request=payload, db=db)
    return success_response(
        data=response,
        message="Error explanation generated",
    )


# ==========================================
# 4. Concept Simplification Interface
# ==========================================
@router.post("/simplify-concept", response_model=ApiResponse[TutorResponse], summary="Simplify DSA concept with analogy")
async def simplify_dsa_concept(
    payload: ConceptSimplificationRequest,
    db: Session = Depends(get_db),
):
    """
    Simplifies an abstract DSA concept using real-world analogies and minimal Java idioms.
    """
    response = await tutor_orchestrator.simplify_dsa_concept(request=payload, db=db)
    return success_response(
        data=response,
        message=f"Concept '{payload.concept_name}' simplified",
    )


# ==========================================
# 5. Practice Question Generation Interface
# ==========================================
@router.post("/practice-questions", response_model=ApiResponse[PracticeQuestionResponse], summary="Generate targeted practice questions")
async def generate_targeted_practice(
    payload: PracticeQuestionRequest,
    db: Session = Depends(get_db),
):
    """
    Generates structured formative questions targeting student's diagnosed cognitive slips.
    """
    response = await tutor_orchestrator.generate_targeted_practice(request=payload, db=db)
    return success_response(
        data=response,
        message=f"Generated {len(response.questions)} practice question(s)",
    )


# ==========================================
# 6. Legacy Scaffolding Route (Backwards Compatibility)
# ==========================================
@router.post("/scaffold", response_model=ApiResponse[ScaffoldingHintResponse], summary="Request progressive scaffolding hint (Legacy)")
async def get_scaffolding_hint(
    payload: ScaffoldingRequest,
    db: Session = Depends(get_db),
):
    """
    Legacy endpoint for progressive hints (Tiers 1-4).
    """
    activity_obj = db.query(Activity).filter(Activity.id == payload.problem_id).first()
    if not activity_obj:
        raise ResourceNotFoundException("Activity", payload.problem_id)

    tier = payload.requested_level or 1

    fallback_templates = {
        "tier_1": f"Reflect on the invariants of {activity_obj.title}. Have you guarded for null or empty edge conditions?",
        "tier_2": "Algorithmic logic: 1. Initialize sentinels. 2. Loop until pointer boundary is reached. 3. Return updated head/state.",
        "tier_3": "State Trace: For input [1, 2, 3], at step 1: current=1, next=2. After reversal: 1.next=null, prev=1.",
        "tier_4": "Skeleton check:\n```java\nListNode next = current.next;\ncurrent.next = prev;\nprev = current;\ncurrent = next;\n```",
    }

    hint_data = await ProgressiveScaffoldingEngine.get_scaffolding_hint(
        tier=tier,
        problem_title=activity_obj.title,
        problem_description=activity_obj.description_md,
        student_code=payload.current_code,
        fallback_content=fallback_templates,
        error_context=payload.compiler_error or payload.failing_test_input,
    )

    log = Intervention(
        student_id=payload.learner_id,
        topic_id=activity_obj.topic_id,
        activity_id=activity_obj.id,
        intervention_type=hint_data["pedagogical_strategy"],
        scaffolding_tier=hint_data["level"],
        trigger_reason="Student Requested Scaffold",
        hint_content=hint_data["hint_text"],
        is_llm_generated=hint_data.get("is_llm_generated", False),
    )
    db.add(log)
    db.commit()

    return success_response(
        data=ScaffoldingHintResponse(**hint_data),
        message=f"Tier {tier} hint generated",
    )


# ==========================================
# 7. Cognitive Misconception Diagnosis Route
# ==========================================
@router.post("/diagnose", response_model=ApiResponse[DiagnosisResponse], summary="Diagnose code misconceptions")
def diagnose_code(payload: DiagnosisRequest):
    """
    Evaluates student code and errors against IT22301 misconception rule catalog.
    """
    diagnosed = diagnostic_engine.diagnose(
        code=payload.code,
        compiler_error=payload.compiler_error or "",
        runtime_error="",
    )

    items = [
        MisconceptionItem(
            rule_code=d["rule_code"],
            name=d["name"],
            severity=d["severity"],
            explanation=d["explanation"],
            suggested_remedy=d["suggested_remedy"],
        )
        for d in diagnosed
    ]

    tier_rec = 1
    if any(item.severity == "Critical" for item in items):
        tier_rec = 2

    return success_response(
        data=DiagnosisResponse(
            misconceptions_detected=items,
            detected_count=len(items),
            recommended_scaffolding_tier=tier_rec,
        ),
        message=f"Diagnosed {len(items)} misconception(s)",
    )
