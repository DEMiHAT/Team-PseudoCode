"""
AI Tutoring Subsystem for IT22301 Data Structures & Algorithms.
Decoupled, Socratic, execution-grounded tutoring using Google Gemini API.
"""

from app.ai_tutor.schemas import (
    TutorContext,
    TutorResponse,
    CodeExecutionEvidence,
    HintRequest,
    ErrorExplanationRequest,
    ConceptSimplificationRequest,
    PracticeQuestionRequest,
    PracticeQuestionResponse,
    PracticeQuestionItem,
    PracticeOption,
)
from app.ai_tutor.gemini_client import GeminiClient, gemini_client
from app.ai_tutor.prompt_templates import (
    SYSTEM_TEACHING_INSTRUCTION,
    build_hint_prompt,
    build_error_explanation_prompt,
    build_concept_simplification_prompt,
    build_practice_question_prompt,
)
from app.ai_tutor.context_retriever import ContextRetriever, context_retriever
from app.ai_tutor.learner_state_bridge import LearnerStateBridge, learner_state_bridge
from app.ai_tutor.error_explainer import ErrorExplainer, error_explainer
from app.ai_tutor.hint_generator import HintGenerator, hint_generator
from app.ai_tutor.concept_simplifier import ConceptSimplifier, concept_simplifier
from app.ai_tutor.practice_generator import PracticeGenerator, practice_generator
from app.ai_tutor.response_validator import ResponseValidator
from app.ai_tutor.orchestrator import TutorOrchestrator, tutor_orchestrator

__all__ = [
    # Schemas
    "TutorContext",
    "TutorResponse",
    "CodeExecutionEvidence",
    "HintRequest",
    "ErrorExplanationRequest",
    "ConceptSimplificationRequest",
    "PracticeQuestionRequest",
    "PracticeQuestionResponse",
    "PracticeQuestionItem",
    "PracticeOption",
    # 1. Gemini API Service
    "GeminiClient",
    "gemini_client",
    # 2. Tutor Orchestration Service
    "TutorOrchestrator",
    "tutor_orchestrator",
    # 3. Structured Prompt Templates
    "SYSTEM_TEACHING_INSTRUCTION",
    "build_hint_prompt",
    "build_error_explanation_prompt",
    "build_concept_simplification_prompt",
    "build_practice_question_prompt",
    # 4. Context Retrieval Interface
    "ContextRetriever",
    "context_retriever",
    # 5. Learner-State Integration
    "LearnerStateBridge",
    "learner_state_bridge",
    # 6. Code-Error Explanation Interface
    "ErrorExplainer",
    "error_explainer",
    # 7. Hint Generation Interface
    "HintGenerator",
    "hint_generator",
    # 8. Concept Simplification Interface
    "ConceptSimplifier",
    "concept_simplifier",
    # 9. Practice Question Generation Interface
    "PracticeGenerator",
    "practice_generator",
    # 10. Response Validation and Error Handling
    "ResponseValidator",
]

