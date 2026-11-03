"""
Code-Error Explanation Interface for AI Tutoring.
Explains verified compiler, runtime, or test execution errors without hallucination.
Distinguishes execution facts from diagnostic hypotheses.
"""

from typing import Optional, Dict, Any
from app.ai_tutor.schemas import TutorContext, TutorResponse
from app.ai_tutor.gemini_client import gemini_client, GeminiClient
from app.ai_tutor.prompt_templates import SYSTEM_TEACHING_INSTRUCTION, build_error_explanation_prompt
from app.ai_tutor.response_validator import ResponseValidator
from app.core.logging import logger


class ErrorExplainer:
    """
    Deconstructs execution failures and runtime exceptions.
    Grounded strictly in actual execution evidence.
    """

    def __init__(self, client: Optional[GeminiClient] = None):
        self.client = client or gemini_client

    async def explain_error(
        self,
        context: TutorContext,
        compiler_error: Optional[str] = None,
        runtime_error: Optional[str] = None,
        failed_test_details: Optional[Dict[str, Any]] = None,
    ) -> TutorResponse:
        """
        Explains an execution discrepancy or syntax error.
        If Gemini is unavailable, provides a deterministic diagnostic explanation.
        """
        # Ensure there is actual error evidence
        has_evidence = bool(
            (compiler_error and compiler_error.strip())
            or (runtime_error and runtime_error.strip())
            or failed_test_details
            or context.execution_evidence.has_evidence
        )

        if not has_evidence:
            return TutorResponse(
                success=True,
                is_fallback=True,
                content="No execution error evidence was provided. Code cannot be evaluated for errors without compiler or test execution output.",
                actionable_next_step="Run the code against the test suite to generate execution evidence.",
                scaffold_level=context.scaffold_level,
                pedagogical_strategy="Execution Requirement Invariant",
                fallback_reason="No error evidence supplied",
            )

        if not self.client.is_configured:
            return ResponseValidator.get_fallback_error_explanation(
                compiler_error=compiler_error,
                runtime_error=runtime_error,
                reason="Gemini API key is unconfigured on the backend.",
            )

        prompt = build_error_explanation_prompt(
            context=context,
            compiler_error=compiler_error,
            runtime_error=runtime_error,
            failed_test_details=failed_test_details,
        )

        try:
            result = await self.client.generate_content(
                prompt=prompt,
                system_instruction=SYSTEM_TEACHING_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=400,
            )

            if result["success"] and result["text"]:
                return ResponseValidator.validate_and_format_error_explanation(result["text"])
            else:
                logger.warning(f"Gemini error explanation failed: {result.get('error')}. Using fallback.")
                return ResponseValidator.get_fallback_error_explanation(
                    compiler_error=compiler_error,
                    runtime_error=runtime_error,
                    reason=result.get("error", "LLM generation returned empty response"),
                )

        except Exception as exc:
            logger.error(f"Unexpected error in ErrorExplainer: {exc}")
            return ResponseValidator.get_fallback_error_explanation(
                compiler_error=compiler_error,
                runtime_error=runtime_error,
                reason=str(exc),
            )


# Singleton instance
error_explainer = ErrorExplainer()
