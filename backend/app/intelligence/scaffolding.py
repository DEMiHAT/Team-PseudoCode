"""
Progressive Scaffolding Engine.
Domain-agnostic cognitive scaffolding model implementing 4 progressive levels of assistance.
Follows Vygotsky's Zone of Proximal Development (ZPD) principle.
"""

from typing import Dict, Any, Optional
from app.services.gemini_service import gemini_service
from app.core.logging import logger


class ProgressiveScaffoldingEngine:
    """
    Manages multi-tier scaffolding assistance.
    Levels:
      Level 1: Conceptual Orientation (Reflective prompt, invariants, constraints)
      Level 2: Algorithmic Blueprint (High-level pseudocode and logic flow)
      Level 3: Concrete State Trace (Input trace and dry run)
      Level 4: Scaffolded Code Skeleton (Targeted code snippet with structured blanks)
    """

    SCAFFOLDING_TIERS = {
        1: {
            "title": "Level 1: Conceptual Orientation",
            "strategy": "Socratic Prompting",
            "description": "Reflect on core invariants and boundary conditions without code spoilers.",
        },
        2: {
            "title": "Level 2: Algorithmic Blueprint",
            "strategy": "Pseudocode Guidance",
            "description": "Examine the logical step-by-step transformation required.",
        },
        3: {
            "title": "Level 3: Concrete State Trace",
            "strategy": "Dry Run Visualization",
            "description": "Trace variable and pointer transitions through sample execution states.",
        },
        4: {
            "title": "Level 4: Code Skeleton & Targeted Fix",
            "strategy": "Structural Scaffolding",
            "description": "A structured code skeleton highlighting the exact missing logic.",
        },
    }

    @classmethod
    async def get_scaffolding_hint(
        cls,
        tier: int,
        problem_title: str,
        problem_description: str,
        student_code: str,
        fallback_content: Dict[str, str],
        misconception_diagnosis: Optional[str] = None,
        error_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves a tier-specific hint. Attempts LLM generation via Gemini if configured,
        otherwise safely falls back to pre-defined pedagogical templates.
        """
        clamped_tier = max(1, min(4, tier))
        tier_meta = cls.SCAFFOLDING_TIERS[clamped_tier]

        # Attempt LLM Socratic generation if configured
        if gemini_service.is_configured:
            llm_result = await gemini_service.generate_socratic_hint(
                problem_title=problem_title,
                problem_description=problem_description,
                student_code=student_code,
                scaffolding_tier=clamped_tier,
                misconception_diagnosis=misconception_diagnosis,
                error_context=error_context,
            )
            if llm_result["success"] and llm_result["hint_text"]:
                return {
                    "level": clamped_tier,
                    "title": tier_meta["title"],
                    "hint_text": llm_result["hint_text"],
                    "code_snippet": None,
                    "is_llm_generated": True,
                    "pedagogical_strategy": tier_meta["strategy"],
                }

        # Deterministic pedagogical fallback
        hint_key = f"tier_{clamped_tier}"
        snippet_key = f"tier_{clamped_tier}_snippet"

        fallback_text = fallback_content.get(
            hint_key,
            f"Review the problem requirements and verify edge cases for {problem_title}.",
        )
        code_snippet = fallback_content.get(snippet_key, None)

        return {
            "level": clamped_tier,
            "title": tier_meta["title"],
            "hint_text": fallback_text,
            "code_snippet": code_snippet,
            "is_llm_generated": False,
            "pedagogical_strategy": tier_meta["strategy"],
        }

