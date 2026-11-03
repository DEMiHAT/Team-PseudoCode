"""
Concept Simplification Interface for AI Tutoring.
Explains complex DSA concepts using intuitive analogies and minimal Java snippets.
Calibrated to the student's mastery level.
"""

from typing import Optional
from app.ai_tutor.schemas import TutorContext, TutorResponse
from app.ai_tutor.gemini_client import gemini_client, GeminiClient
from app.ai_tutor.prompt_templates import SYSTEM_TEACHING_INSTRUCTION, build_concept_simplification_prompt
from app.ai_tutor.response_validator import ResponseValidator
from app.core.logging import logger


class ConceptSimplifier:
    """
    Translates abstract data structures and algorithmic invariants
    into intuitive conceptual models and simple Java demonstrations.
    """

    def __init__(self, client: Optional[GeminiClient] = None):
        self.client = client or gemini_client

    async def simplify_concept(
        self,
        context: TutorContext,
        concept_name: str,
        student_question: Optional[str] = None,
        analogy_domain: str = "everyday physical systems",
    ) -> TutorResponse:
        """
        Generates an intuitive explanation with real-world analogies and concise Java code.
        """
        if not self.client.is_configured:
            return ResponseValidator.get_fallback_simplification(
                concept_name=concept_name,
                reason="Gemini API key is unconfigured on the backend.",
            )

        prompt = build_concept_simplification_prompt(
            context=context,
            concept_name=concept_name,
            student_question=student_question,
            analogy_domain=analogy_domain,
        )

        try:
            result = await self.client.generate_content(
                prompt=prompt,
                system_instruction=SYSTEM_TEACHING_INSTRUCTION,
                temperature=0.3,
                max_output_tokens=450,
            )

            if result["success"] and result["text"]:
                return ResponseValidator.validate_and_format_simplification(
                    llm_text=result["text"],
                    concept_name=concept_name,
                )
            else:
                logger.warning(f"Gemini concept simplification failed: {result.get('error')}. Using fallback.")
                return ResponseValidator.get_fallback_simplification(
                    concept_name=concept_name,
                    reason=result.get("error", "LLM generation returned empty response"),
                )

        except Exception as exc:
            logger.error(f"Unexpected error in ConceptSimplifier: {exc}")
            return ResponseValidator.get_fallback_simplification(
                concept_name=concept_name,
                reason=str(exc),
            )


# Singleton instance
concept_simplifier = ConceptSimplifier()
