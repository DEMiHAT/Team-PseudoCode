"""
Tutor Orchestration Service for IT22301 DSA Learning Platform.
Acts as the central conductor for contextual retrieval, LLM interaction,
response validation, and pedagogical intervention logging.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.ai_tutor.schemas import (
    TutorContext,
    TutorResponse,
    CodeExecutionEvidence,
    PracticeQuestionResponse,
    HintRequest,
    ErrorExplanationRequest,
    ConceptSimplificationRequest,
    PracticeQuestionRequest,
)
from app.ai_tutor.context_retriever import context_retriever, ContextRetriever
from app.ai_tutor.gemini_client import gemini_client, GeminiClient
from app.ai_tutor.hint_generator import hint_generator, HintGenerator
from app.ai_tutor.error_explainer import error_explainer, ErrorExplainer
from app.ai_tutor.concept_simplifier import concept_simplifier, ConceptSimplifier
from app.ai_tutor.practice_generator import practice_generator, PracticeGenerator
from app.models.intervention import Intervention
from app.core.logging import logger


class TutorOrchestrator:
    """
    Central orchestration service for AI-assisted DSA tutoring.
    Ensures consistent context ingestion, guardrail enforcement, and intervention auditing.
    """

    def __init__(
        self,
        retriever: Optional[ContextRetriever] = None,
        client: Optional[GeminiClient] = None,
        hints: Optional[HintGenerator] = None,
        explainer: Optional[ErrorExplainer] = None,
        simplifier: Optional[ConceptSimplifier] = None,
        practice: Optional[PracticeGenerator] = None,
    ):
        self.retriever = retriever or context_retriever
        self.client = client or gemini_client
        self.hints = hints or HintGenerator(client=self.client)
        self.explainer = explainer or ErrorExplainer(client=self.client)
        self.simplifier = simplifier or ConceptSimplifier(client=self.client)
        self.practice = practice or PracticeGenerator(client=self.client)

    async def get_health_status(self) -> Dict[str, Any]:
        """Returns the operational status of the AI tutoring subsystem."""
        client_health = await self.client.check_health()
        return {
            "orchestrator_status": "ready",
            "gemini_api": client_health,
            "teaching_invariants_enforced": True,
            "fallback_engine_available": True,
        }

    async def provide_scaffolded_hint(
        self,
        request: HintRequest,
        db: Optional[Session] = None,
    ) -> TutorResponse:
        """
        Orchestrates progressive hint generation:
        1. Assembles multi-skill context.
        2. Queries hint generation interface (or deterministic fallback).
        3. Persists intervention log into DB for efficacy auditing.
        """
        has_exec = bool(
            request.execution_status
            or request.compiler_error
            or request.runtime_error
            or request.failing_input
        )
        evidence = CodeExecutionEvidence(
            has_evidence=has_exec,
            status=request.execution_status,
            stderr=request.compiler_error or request.runtime_error,
            failed_test_case={"input": request.failing_input} if request.failing_input else None,
        )

        context = self.retriever.build_context(
            student_id=request.student_id,
            db=db,
            topic_id=request.topic_id,
            activity_id=request.activity_id,
            scaffold_level=request.scaffold_level,
            current_code=request.current_code,
            execution_evidence=evidence,
        )

        response = await self.hints.generate_hint(context)

        # Audit intervention event in DB if session is active
        if db is not None:
            self._log_intervention(
                db=db,
                student_id=request.student_id,
                topic_id=request.topic_id or 1,
                activity_id=request.activity_id,
                tier=response.scaffold_level,
                strategy=response.pedagogical_strategy,
                content=response.content,
                is_llm_generated=not response.is_fallback,
            )

        return response

    async def explain_code_error(
        self,
        request: ErrorExplanationRequest,
        db: Optional[Session] = None,
    ) -> TutorResponse:
        """
        Orchestrates grounded code error explanations without hallucinated defects.
        """
        has_exec = bool(request.compiler_error or request.runtime_error or request.failing_test_details)
        evidence = CodeExecutionEvidence(
            has_evidence=has_exec,
            status="Compilation Error" if request.compiler_error else "Runtime Error",
            stderr=request.compiler_error or request.runtime_error,
            failed_test_case=request.failing_test_details,
        )

        context = self.retriever.build_context(
            student_id=request.student_id,
            db=db,
            topic_id=request.topic_id,
            activity_id=request.activity_id,
            current_code=request.code,
            execution_evidence=evidence,
        )

        response = await self.explainer.explain_error(
            context=context,
            compiler_error=request.compiler_error,
            runtime_error=request.runtime_error,
            failed_test_details=request.failing_test_details,
        )

        if db is not None:
            self._log_intervention(
                db=db,
                student_id=request.student_id,
                topic_id=request.topic_id or 1,
                activity_id=request.activity_id,
                tier=2,
                strategy="Code Error Diagnosis",
                content=response.content,
                is_llm_generated=not response.is_fallback,
            )

        return response

    async def simplify_dsa_concept(
        self,
        request: ConceptSimplificationRequest,
        db: Optional[Session] = None,
    ) -> TutorResponse:
        """
        Orchestrates pedagogical concept simplification via analogical reasoning.
        """
        context = self.retriever.build_context(
            student_id=request.student_id,
            db=db,
        )

        return await self.simplifier.simplify_concept(
            context=context,
            concept_name=request.concept_name,
            student_question=request.student_question,
            analogy_domain=request.target_analogy_domain or "everyday physical systems",
        )

    async def generate_targeted_practice(
        self,
        request: PracticeQuestionRequest,
        db: Optional[Session] = None,
    ) -> PracticeQuestionResponse:
        """
        Generates structured formative questions targeting student's specific gaps.
        """
        context = self.retriever.build_context(
            student_id=request.student_id,
            db=db,
            topic_id=request.topic_id,
        )

        return await self.practice.generate_practice_questions(
            context=context,
            target_concept=request.target_concept,
            difficulty=request.difficulty or "Intermediate",
            count=request.count,
        )

    @staticmethod
    def _log_intervention(
        db: Session,
        student_id: int,
        topic_id: int,
        activity_id: Optional[int],
        tier: int,
        strategy: str,
        content: str,
        is_llm_generated: bool,
    ) -> None:
        """Safely records an intervention event."""
        try:
            log = Intervention(
                student_id=student_id,
                topic_id=topic_id,
                activity_id=activity_id,
                intervention_type=strategy[:60],
                scaffolding_tier=tier,
                trigger_reason="AI Tutor Assistance Request",
                hint_content=content,
                is_llm_generated=is_llm_generated,
            )
            db.add(log)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.warning(f"Could not persist intervention log: {exc}")


# Singleton instance
tutor_orchestrator = TutorOrchestrator()
