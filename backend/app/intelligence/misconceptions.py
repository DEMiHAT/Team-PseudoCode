"""
Misconception Diagnosis Module.
Evaluates student cognitive bugs across attempts using configurable rules.
CRITICAL INVARIANT: A single mistake is NEVER treated as a confirmed misconception.
Requires repeated evidence accumulation across attempts or multiple test vectors to confirm.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.intelligence.error_classifier import ClassifiedError, ErrorCategory


class MisconceptionStatus(str):
    CANDIDATE = "candidate"     # Observed once; unconfirmed hypothesis
    CONFIRMED = "confirmed"     # Repeatedly demonstrated across attempts (>= threshold)
    RESOLVED = "resolved"       # Successfully fixed on subsequent attempts


class MisconceptionRecord(BaseModel):
    """Tracks a student's misconception lifecycle with objective evidence."""
    rule_code: str
    name: str
    status: str = MisconceptionStatus.CANDIDATE
    observation_count: int = 1
    evidence_trail: List[str] = Field(default_factory=list)
    first_observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    explanation: str
    suggested_remedy: str


class CognitiveMisconceptionDiagnoser:
    """
    Diagnoses underlying student cognitive traps from practical error signatures.
    Implements an evidence accumulator:
      - Count = 1: Candidate Misconception (requires corroboration)
      - Count >= 2: Confirmed Misconception (promoted for targeted intervention)
    """

    CONFIRMATION_THRESHOLD = 2

    # Configurable Catalog of Cognitive Misconceptions for Data Structures & Algorithms
    RULES_CATALOG: Dict[str, Dict[str, str]] = {
        "MISC-EMPTY-POP": {
            "name": "Eager Popping on Empty Stack",
            "explanation": "Belief that every bracket string is well-formed, omitting the check for whether a closing bracket arrives when the stack is already empty.",
            "remedy": "Before attempting to pop or peek, explicitly verify `if (stack.isEmpty()) return false;`.",
        },
        "MISC-FIFO-NOT-LIFO": {
            "name": "FIFO Assumption on LIFO Structure",
            "explanation": "Treating the stack as a queue or checking brackets in left-to-right arrival order rather than innermost-first correspondence.",
            "remedy": "Remember LIFO: the most recently opened bracket must be the very first one closed.",
        },
        "MISC-NESTED-INTERLEAVE": {
            "name": "Type-Agnostic Bracket Matching",
            "explanation": "Assuming balanced bracket count suffices, without enforcing that opening and closing brackets of differing types cannot interleave (e.g. '([)]').",
            "remedy": "When matching, verify that `c == ')'` only closes `'('`, `']'` only closes `'['`, and `'}'` only closes `'{'`. Pairs cannot overlap.",
        },
        "MISC-MISSING-TERMINAL-CHECK": {
            "name": "Premature Success on Partial Match",
            "explanation": "Assuming valid traversal means the string is valid, neglecting that leftover unclosed opening brackets on the stack render it invalid.",
            "remedy": "At the conclusion of the method, return `stack.isEmpty()` rather than unconditionally returning `true`.",
        },
        "MISC-REPEATED-SYNTAX-SLIP": {
            "name": "Generic Type / Primitive Confusion",
            "explanation": "Repeatedly using primitive types `char` inside Java Collections generic brackets `Stack<char>`.",
            "remedy": "Java Collections require reference objects. Use `Stack<Character>` instead of primitive `char`.",
        },
    }

    @classmethod
    def evaluate_errors(
        cls,
        classified_errors: List[ClassifiedError],
        existing_history: Optional[Dict[str, MisconceptionRecord]] = None,
    ) -> Dict[str, MisconceptionRecord]:
        """
        Processes current classified errors and updates the student's cognitive state.
        Promotes candidates to confirmed ONLY when evidence count >= 2.
        """
        history = existing_history.copy() if existing_history else {}
        now = datetime.now(timezone.utc)

        for err in classified_errors:
            rule_code = cls._map_error_to_rule(err)
            if not rule_code:
                continue

            rule_meta = cls.RULES_CATALOG[rule_code]
            evidence_item = f"Input: {err.affected_test_input or 'syntax'} -> {err.title}"

            if rule_code in history:
                rec = history[rule_code]
                rec.observation_count += 1
                rec.last_observed_at = now
                if evidence_item not in rec.evidence_trail:
                    rec.evidence_trail.append(evidence_item)

                # Promotion check: requires >= 2 occurrences to confirm
                if rec.observation_count >= cls.CONFIRMATION_THRESHOLD:
                    rec.status = MisconceptionStatus.CONFIRMED
            else:
                # First observation: candidate only (NOT confirmed)
                history[rule_code] = MisconceptionRecord(
                    rule_code=rule_code,
                    name=rule_meta["name"],
                    status=MisconceptionStatus.CANDIDATE,
                    observation_count=1,
                    evidence_trail=[evidence_item],
                    first_observed_at=now,
                    last_observed_at=now,
                    explanation=rule_meta["explanation"],
                    suggested_remedy=rule_meta["remedy"],
                )

        return history

    @classmethod
    def mark_resolved_misconceptions(
        cls,
        history: Dict[str, MisconceptionRecord],
        successful_run: bool,
    ) -> Dict[str, MisconceptionRecord]:
        """Marks active misconceptions as resolved when the student demonstrates clean independent mastery."""
        if not successful_run:
            return history

        for rec in history.values():
            if rec.status in (MisconceptionStatus.CANDIDATE, MisconceptionStatus.CONFIRMED):
                rec.status = MisconceptionStatus.RESOLVED

        return history

    @classmethod
    def _map_error_to_rule(cls, err: ClassifiedError) -> Optional[str]:
        """Maps classified runtime/test errors to cognitive rule codes."""
        if err.category == ErrorCategory.EMPTY_STACK_ACCESS:
            return "MISC-EMPTY-POP"
        elif err.category == ErrorCategory.NESTED_BRACKET:
            return "MISC-NESTED-INTERLEAVE"
        elif err.category == ErrorCategory.INVARIANT_VIOLATION:
            return "MISC-MISSING-TERMINAL-CHECK"
        elif err.category == ErrorCategory.MATCHING_ORDER:
            return "MISC-FIFO-NOT-LIFO"
        elif err.category == ErrorCategory.COMPILATION and "incompatible types" in (err.evidence_snippet or "").lower():
            return "MISC-REPEATED-SYNTAX-SLIP"
        return None


misconception_diagnoser = CognitiveMisconceptionDiagnoser()
