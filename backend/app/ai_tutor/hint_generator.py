"""
Hint Generation Interface for AI Tutoring.
Generates scaffold-aligned, Socratic hints (L1-L5) with strictly one actionable step.
Respects active scaffolding level and never reveals complete solutions prematurely.
"""

from typing import Optional
from app.ai_tutor.schemas import TutorContext, TutorResponse
from app.ai_tutor.gemini_client import gemini_client, GeminiClient
from app.ai_tutor.prompt_templates import SYSTEM_TEACHING_INSTRUCTION, build_hint_prompt
from app.ai_tutor.response_validator import ResponseValidator
from app.core.logging import logger


class HintGenerator:
    """
    Produces progressive hints respecting student cognitive mastery
    and assigned scaffolding levels.
    """

    def __init__(self, client: Optional[GeminiClient] = None):
        self.client = client or gemini_client

    async def generate_hint(self, context: TutorContext) -> TutorResponse:
        """
        Generates an adaptive hint. If Gemini is unconfigured or encounters an error,
        delivers a deterministic curriculum fallback with zero interruption.
        """
        if not self.client.is_configured:
            return ResponseValidator.get_fallback_hint(
                scaffold_level=context.scaffold_level,
                reason="Gemini API key is not configured on the server.",
            )

        prompt = build_hint_prompt(context)

        try:
            result = await self.client.generate_content(
                prompt=prompt,
                system_instruction=SYSTEM_TEACHING_INSTRUCTION,
                temperature=0.3,
                max_output_tokens=350,
            )

            if result["success"] and result["text"]:
                strategy = f"Tier {context.scaffold_level} Socratic Guidance"
                return ResponseValidator.validate_and_format_hint(
                    llm_text=result["text"],
                    scaffold_level=context.scaffold_level,
                    pedagogical_strategy=strategy,
                )
            else:
                logger.warning(f"Gemini hint generation failed: {result.get('error')}. Using fallback.")
                return ResponseValidator.get_fallback_hint(
                    scaffold_level=context.scaffold_level,
                    reason=result.get("error", "LLM generation returned empty response"),
                )

        except Exception as exc:
            logger.error(f"Unexpected exception in HintGenerator: {exc}")
            return ResponseValidator.get_fallback_hint(
                scaffold_level=context.scaffold_level,
                reason=str(exc),
            )


# Singleton instance
hint_generator = HintGenerator()

