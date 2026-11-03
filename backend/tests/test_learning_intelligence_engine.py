"""
Comprehensive Unit Test Suite for the Learning Intelligence Engine.
Tests all 7 components:
1. Bayesian Knowledge Tracing (4 distinct skills)
2. Practical Error Classification
3. Cognitive Misconception Diagnosis (Candidate vs Confirmed thresholding)
4. 6-Level Progressive Scaffolding (L0 to L5)
5. Adaptive Intervention Selection (Multi-factor explainability)
6. Learner State Management (Decoupled from LLMs)
7. Intervention Outcome Logging & Bandit Reward Signals
"""

import pytest
from app.intelligence.bkt import (
    BayesianKnowledgeTracer,
    SkillType,
    SkillParameters,
    bkt_engine,
)
from app.intelligence.error_classifier import (
    PracticalErrorClassifier,
    ErrorCategory,
    ErrorSeverity,
    error_classifier,
)
from app.intelligence.misconceptions import (
    CognitiveMisconceptionDiagnoser,
    MisconceptionStatus,
    misconception_diagnoser,
)
from app.intelligence.scaffolding import (
    ProgressiveScaffoldingEngine,
    ScaffoldingLevel,
    scaffolding_engine,
)
from app.intelligence.intervention import (
    AdaptiveInterventionSelector,
    InterventionDecision,
    intervention_selector,
)
from app.intelligence.state_manager import (
    LearnerStateManager,
    learner_state_manager,
)
from app.intelligence.outcome_logger import (
    InterventionOutcomeLogger,
    InterventionLifecycleRecord,
    outcome_logger,
)


# ==============================================================================
# 1. BAYESIAN KNOWLEDGE TRACING (BKT) TESTS
# ==============================================================================

def test_bkt_all_four_distinct_skills_registered():
    """Verify that all 4 required skills exist with distinct calibrated parameters."""
    skills = [
        SkillType.STACK_CONCEPTUAL,
        SkillType.STACK_JAVA_IMPL,
        SkillType.STACK_UNDERFLOW,
        SkillType.PARENTHESES_VALIDATION,
    ]
    for s in skills:
        params = bkt_engine.get_skill_params(s)
        assert 0.0 < params.p_init < 1.0
        assert 0.0 < params.p_transit < 1.0
        assert 0.0 < params.p_guess < 1.0
        assert 0.0 < params.p_slip < 1.0
        assert params.mastery_threshold >= 0.85


def test_bkt_correct_answer_updates():
    """Correct answers must increase cognitive mastery belief strictly via Bayesian equations."""
    tracer = BayesianKnowledgeTracer()
    prior = 0.20
    result = tracer.update_skill(SkillType.STACK_UNDERFLOW, prior, is_correct=True)

    assert result.next_prior_p_known > prior
    assert result.posterior_p_known > prior
    assert 0.0 <= result.next_prior_p_known <= 1.0
    assert result.is_correct is True


def test_bkt_incorrect_answer_updates():
    """Incorrect answers must dampen cognitive mastery belief."""
    tracer = BayesianKnowledgeTracer()
    prior = 0.60
    result = tracer.update_skill(SkillType.PARENTHESES_VALIDATION, prior, is_correct=False)

    assert result.posterior_p_known < prior
    assert result.is_correct is False


def test_bkt_multi_skill_independence():
    """Updating one skill does not artificially contaminate or collapse another skill."""
    tracer = BayesianKnowledgeTracer()
    current_skills = {
        SkillType.STACK_JAVA_IMPL: 0.20,
        SkillType.STACK_UNDERFLOW: 0.20,
    }
    evidence = {
        SkillType.STACK_JAVA_IMPL: True,   # Compilation succeeded
        SkillType.STACK_UNDERFLOW: False,  # Runtime empty stack failure
    }
    updates = tracer.update_multi_skill(current_skills, evidence)

    assert updates[SkillType.STACK_JAVA_IMPL.value].next_prior_p_known > 0.20
    assert updates[SkillType.STACK_UNDERFLOW.value].posterior_p_known < 0.20


# ==============================================================================
# 2. PRACTICAL ERROR CLASSIFICATION TESTS
# ==============================================================================

def test_classify_empty_stack_access():
    """Detects underflow when pop() is called on empty stack."""
    failures = [{
        "input": '"]"',
        "expected": "false",
        "actual": None,
        "error": "java.util.EmptyStackException",
    }]
    errors = error_classifier.classify_execution(
        code="stack.pop();",
        stderr="Exception: java.util.EmptyStackException",
        test_failures=failures,
    )
    categories = [e.category for e in errors]
    assert ErrorCategory.EMPTY_STACK_ACCESS in categories


def test_classify_nested_bracket_order():
    """Detects invalid bracket nesting order failures (e.g. '([)]')."""
    failures = [{
        "input": '"([)]"',
        "expected": "false",
        "actual": "true",
    }]
    errors = error_classifier.classify_execution(
        code="...",
        test_failures=failures,
    )
    categories = [e.category for e in errors]
    assert ErrorCategory.NESTED_BRACKET in categories


def test_classify_compilation_error():
    """Detects Java compilation issues such as unresolved symbol or generic types."""
    compile_err = "Solution.java:5: error: cannot find symbol class Stack"
    errors = error_classifier.classify_execution(
        code="Stack<Character> s;",
        compile_output=compile_err,
    )
    assert len(errors) >= 1
    assert errors[0].category == ErrorCategory.COMPILATION
    assert errors[0].severity == ErrorSeverity.CRITICAL


# ==============================================================================
# 3. MISCONCEPTION ACCUMULATION & INVARIANT TESTS
# ==============================================================================

def test_single_error_is_never_confirmed_misconception():
    """
    CRITICAL REQUIREMENT: A single error MUST remain a Candidate,
    and is NEVER treated as a Confirmed Misconception until corroborating evidence is seen.
    """
    failures = [{"input": '"]"', "expected": "false", "actual": None, "error": "EmptyStackException"}]
    errors = error_classifier.classify_execution(code="stack.pop();", test_failures=failures)

    history = misconception_diagnoser.evaluate_errors(classified_errors=errors)
    record = history.get("MISC-EMPTY-POP")

    assert record is not None
    assert record.observation_count == 1
    # MUST be candidate, NOT confirmed!
    assert record.status == MisconceptionStatus.CANDIDATE


def test_repeated_error_promotes_to_confirmed_misconception():
    """When an error is repeated across attempts (count >= 2), it is promoted to Confirmed."""
    failures = [{"input": '"]"', "expected": "false", "actual": None, "error": "EmptyStackException"}]
    errors = error_classifier.classify_execution(code="stack.pop();", test_failures=failures)

    # 1st attempt: candidate
    history = misconception_diagnoser.evaluate_errors(classified_errors=errors)
    assert history["MISC-EMPTY-POP"].status == MisconceptionStatus.CANDIDATE

    # 2nd attempt with same cognitive slip: corroborating evidence promotes to confirmed!
    history = misconception_diagnoser.evaluate_errors(classified_errors=errors, existing_history=history)
    record = history["MISC-EMPTY-POP"]

    assert record.observation_count == 2
    assert record.status == MisconceptionStatus.CONFIRMED


# ==============================================================================
# 4. SIX-LEVEL PROGRESSIVE SCAFFOLDING TESTS (L0 to L5)
# ==============================================================================

def test_six_levels_of_scaffolding():
    """Verify all 6 scaffolding tiers (L0 to L5) produce calibrated pedagogical content."""
    levels = [
        (ScaffoldingLevel.L0_INDEPENDENT, "L0", True),
        (ScaffoldingLevel.L1_CONCEPTUAL_PROMPT, "L1", False),
        (ScaffoldingLevel.L2_TARGETED_HINT, "L2", False),
        (ScaffoldingLevel.L3_ALGORITHM_GUIDE, "L3", False),
        (ScaffoldingLevel.L4_PARTIAL_IMPL, "L4", False),
        (ScaffoldingLevel.L5_WORKED_SOLUTION, "L5", False),
    ]

    for lvl, tag, is_indep in levels:
        scaffold = scaffolding_engine.get_scaffolding(lvl)
        assert scaffold.level == lvl.value
        assert tag in scaffold.level_name
        assert len(scaffold.prompt_text) > 20
        assert scaffold.is_independent == is_indep

        # L3 must contain pseudocode
        if lvl == ScaffoldingLevel.L3_ALGORITHM_GUIDE:
            assert scaffold.pseudocode is not None

        # L4 and L5 must contain code templates
        if lvl in (ScaffoldingLevel.L4_PARTIAL_IMPL, ScaffoldingLevel.L5_WORKED_SOLUTION):
            assert scaffold.code_template is not None
            assert "class Solution" in scaffold.code_template


# ==============================================================================
# 5. ADAPTIVE INTERVENTION SELECTION TESTS
# ==============================================================================

def test_intervention_preserves_initial_independent_attempt():
    """Attempt 1 without compiler error must present L0 Independent attempt."""
    decision = intervention_selector.select_intervention(
        skill_mastery={"stack_conceptual": 0.20},
        misconception_history={},
        activity_attempt_count=1,
        current_scaffolding_level=0,
        independent_success_ratio=0.5,
    )
    assert decision.selected_level == ScaffoldingLevel.L0_INDEPENDENT
    assert "independent" in decision.decision_rationale.lower()


def test_intervention_escalates_on_persistent_confirmed_misconception():
    """When a confirmed misconception persists after prior failure, escalate to L4 Partial Implementation."""
    # Create a confirmed misconception
    from app.intelligence.misconceptions import MisconceptionRecord
    confirmed_misc = {
        "MISC-EMPTY-POP": MisconceptionRecord(
            rule_code="MISC-EMPTY-POP",
            name="Eager Popping on Empty Stack",
            status=MisconceptionStatus.CONFIRMED,
            observation_count=2,
            explanation="Omitted empty stack check",
            suggested_remedy="Check isEmpty()",
        )
    }

    decision = intervention_selector.select_intervention(
        skill_mastery={"stack_underflow": 0.15},
        misconception_history=confirmed_misc,
        activity_attempt_count=3,
        current_scaffolding_level=2,
        independent_success_ratio=0.2,
        last_intervention_successful=False,  # Prior hint did not help
    )

    assert decision.selected_level == ScaffoldingLevel.L4_PARTIAL_IMPL
    assert "confirmed misconception" in decision.decision_rationale.lower()
    assert decision.feature_vector["confirmed_misc_count"] == 1.0


# ==============================================================================
# 6. LEARNER STATE MANAGER TESTS (DECISION EXPLAINABILITY & NO-LLM INVARIANT)
# ==============================================================================

def test_state_manager_evaluates_evidence_without_llm():
    """Verify that state updates are driven by test evidence and BKT mathematics, not LLM scores."""
    state = learner_state_manager.initialize_state(student_id=42)
    assert len(state.skills) == 4

    # Simulate submission with empty stack access
    result = learner_state_manager.process_submission_evidence(
        state=state,
        activity_id=1,
        code="stack.pop();",
        is_passed=False,
        was_assisted=False,
        stderr="java.util.EmptyStackException",
        test_failures=[{"input": '"]"', "expected": "false", "actual": None, "error": "EmptyStackException"}],
    )

    assert result["is_passed"] is False
    assert SkillType.STACK_UNDERFLOW.value in result["bkt_updates"]
    # Evidence is explainable and deterministic
    assert len(result["classified_errors"]) >= 1
    assert result["recommended_intervention"] is not None


# ==============================================================================
# 7. INTERVENTION OUTCOME LOGGING & BANDIT REWARD TESTS
# ==============================================================================

def test_outcome_logging_calculates_bandit_rewards():
    """Verify that subsequent attempt performance computes correct normalized reward signals."""
    record = InterventionLifecycleRecord(
        intervention_id="int-101",
        student_id=42,
        activity_id=1,
        target_skill="stack_underflow",
        scaffolding_tier=2,
        trigger_reason="underflow_detected",
        decision_rationale="Tested targeted hint",
    )

    # Outcome A: Independent success on subsequent attempt -> High Reward (+1.0)
    evaluated_record = outcome_logger.record_outcome(
        intervention=record,
        attempt_id=2,
        is_passed=True,
        was_assisted=False,
    )
    assert evaluated_record.efficacy_score == 1.0
    assert evaluated_record.subsequent_attempt_independent is True

    # Outcome B: Persistent failure -> Negative Reward (-0.5)
    evaluated_fail = outcome_logger.record_outcome(
        intervention=record,
        attempt_id=3,
        is_passed=False,
        was_assisted=False,
    )
    assert evaluated_fail.efficacy_score == -0.5
