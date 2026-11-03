"""
Adaptive Tutoring and Scaffolding Routes.
Provides progressive hints (Tiers 1-4) and rule-based misconception diagnoses.
"""

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
from app.intelligence.scaffolding import ProgressiveScaffoldingEngine
from app.intelligence.misconception_engine import MisconceptionEngine
from app.content.dsa_misconceptions import get_default_dsa_rules
from app.utilities.response import ApiResponse, success_response
from app.utilities.exceptions import ResourceNotFoundException

router = APIRouter()
diagnostic_engine = MisconceptionEngine(rules=get_default_dsa_rules())


@router.post("/scaffold", response_model=ApiResponse[ScaffoldingHintResponse], summary="Request progressive scaffolding hint")
async def get_scaffolding_hint(
    payload: ScaffoldingRequest,
    db: Session = Depends(get_db),
):
    """
    Returns a progressive hint based on requested or calculated tier (1 to 4).
    Uses Gemini if configured, otherwise falls back to deterministic curriculum templates.
    Logs intervention event for pedagogical efficacy auditing.
    """
    activity_obj = db.query(Activity).filter(Activity.id == payload.problem_id).first()
    if not activity_obj:
        raise ResourceNotFoundException("Activity", payload.problem_id)

    tier = payload.requested_level or 1

    # Fallback pedagogical content tailored for DSA
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

    # Persist Intervention record for efficacy analytics
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
