"""
Practice Question Generation Interface for AI Tutoring.
Produces targeted formative assessment items calibrated to the learner's diagnosed cognitive slips.
Outputs validated, structured question models with explanations.
"""

from typing import Optional
from app.ai_tutor.schemas import TutorContext, PracticeQuestionResponse
from app.ai_tutor.gemini_client import gemini_client, GeminiClient
from app.ai_tutor.prompt_templates import SYSTEM_TEACHING_INSTRUCTION, build_practice_question_prompt
from app.ai_tutor.response_validator import ResponseValidator
from app.core.logging import logger


class PracticeGenerator:
    """
    Creates dynamic, concept-targeted practice items formatted as strict JSON.
    """

    def __init__(self, client: Optional[GeminiClient] = None):
        self.client = client or gemini_client

    async def generate_practice_questions(
        self,
        context: TutorContext,
        target_concept: Optional[str] = None,
        difficulty: str = "Intermediate",
        count: int = 1,
    ) -> PracticeQuestionResponse:
        """
        Requests structured formative questions targeting specific weak concepts.
        """
        concept = target_concept or context.topic

        if not self.client.is_configured:
            return ResponseValidator.get_fallback_practice_questions(
                target_concept=concept,
                reason="Gemini API key is unconfigured on the backend.",
            )

        prompt = build_practice_question_prompt(
            context=context,
            target_concept=concept,
            difficulty=difficulty,
            count=count,
        )

        try:
            result = await self.client.generate_content(
                prompt=prompt,
                system_instruction=SYSTEM_TEACHING_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=700,
                response_mime_type="application/json",
            )

            if result["success"] and result["text"]:
                return ResponseValidator.validate_and_format_practice_questions(
                    llm_text=result["text"],
                    target_concept=concept,
                )
            else:
                logger.warning(f"Gemini practice generation failed: {result.get('error')}. Using fallback.")
                return ResponseValidator.get_fallback_practice_questions(
                    target_concept=concept,
                    reason=result.get("error", "LLM generation returned empty response"),
                )

        except Exception as exc:
            logger.error(f"Unexpected error in PracticeGenerator: {exc}")
            return ResponseValidator.get_fallback_practice_questions(
                target_concept=concept,
                reason=str(exc),
            )


# Singleton instance
practice_generator = PracticeGenerator()

