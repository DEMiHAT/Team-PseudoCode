"""
Reusable Learning Intelligence Engine Package.
Comprises 7 independent, decoupled cognitive modules:
1. Bayesian Knowledge Tracing (BKT)
2. Practical Error Classification
3. Cognitive Misconception Diagnosis
4. Progressive Scaffolding (6 Tiers: L0-L5)
5. Adaptive Intervention Selection
6. Learner State Management
7. Intervention Outcome Logging & Efficacy
"""

from app.intelligence.bkt import (
    BayesianKnowledgeTracer,
    SkillType,
    SkillParameters,
    BKTUpdateResult,
    bkt_engine,
)
from app.intelligence.error_classifier import (
    PracticalErrorClassifier,
    ClassifiedError,
    ErrorCategory,
    ErrorSeverity,
    error_classifier,
)
from app.intelligence.misconceptions import (
    CognitiveMisconceptionDiagnoser,
    MisconceptionRecord,
    MisconceptionStatus,
    misconception_diagnoser,
)
from app.intelligence.scaffolding import (
    ProgressiveScaffoldingEngine,
    ScaffoldingLevel,
    ScaffoldingPayload,
    scaffolding_engine,
)
from app.intelligence.intervention import (
    AdaptiveInterventionSelector,
    InterventionDecision,
    intervention_selector,
)
from app.intelligence.state_manager import (
    LearnerStateManager,
    LearnerCognitiveState,
    SkillStateSnapshot,
    learner_state_manager,
)
from app.intelligence.outcome_logger import (
    InterventionOutcomeLogger,
    InterventionLifecycleRecord,
    outcome_logger,
)

# Backwards compatibility aliases
BKTEngine = bkt_engine

__all__ = [
    "BayesianKnowledgeTracer",
    "SkillType",
    "SkillParameters",
    "BKTUpdateResult",
    "bkt_engine",
    "BKTEngine",
    "PracticalErrorClassifier",
    "ClassifiedError",
    "ErrorCategory",
    "ErrorSeverity",
    "error_classifier",
    "CognitiveMisconceptionDiagnoser",
    "MisconceptionRecord",
    "MisconceptionStatus",
    "misconception_diagnoser",
    "ProgressiveScaffoldingEngine",
    "ScaffoldingLevel",
    "ScaffoldingPayload",
    "scaffolding_engine",
    "AdaptiveInterventionSelector",
    "InterventionDecision",
    "intervention_selector",
    "LearnerStateManager",
    "LearnerCognitiveState",
    "SkillStateSnapshot",
    "learner_state_manager",
    "InterventionOutcomeLogger",
    "InterventionLifecycleRecord",
    "outcome_logger",
]
