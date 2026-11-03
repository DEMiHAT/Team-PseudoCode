"""
Misconception Engine.
Domain-agnostic cognitive diagnosis architecture.
Executes declarative rule evaluation over student code, error logs, and execution traces.
"""

from typing import List, Dict, Any, Optional
import re


class MisconceptionRule:
    """Represents a discrete pedagogical bug rule."""

    def __init__(
        self,
        rule_code: str,
        name: str,
        severity: str,
        explanation: str,
        suggested_remedy: str,
        matcher_pattern: Optional[str] = None,
        runtime_keyword: Optional[str] = None,
    ):
        self.rule_code = rule_code
        self.name = name
        self.severity = severity  # Critical, Warning, LogicError
        self.explanation = explanation
        self.suggested_remedy = suggested_remedy
        self.matcher_pattern = matcher_pattern
        self.runtime_keyword = runtime_keyword

    def evaluate(self, code: str, error_text: str = "") -> bool:
        """Evaluates whether this misconception signature is present."""
        # 1. Check runtime error keywords (e.g. NullPointerException, ArrayIndexOutOfBoundsException)
        if self.runtime_keyword and self.runtime_keyword.lower() in error_text.lower():
            return True

        # 2. Check regex patterns in student code
        if self.matcher_pattern:
            try:
                if re.search(self.matcher_pattern, code, re.IGNORECASE):
                    return True
            except re.error:
                pass

        return False


class MisconceptionEngine:
    """Executes cognitive rules to diagnose student conceptual hurdles."""

    def __init__(self, rules: Optional[List[MisconceptionRule]] = None):
        self.rules: List[MisconceptionRule] = rules or []

    def register_rule(self, rule: MisconceptionRule) -> None:
        """Registers a new diagnostic rule."""
        self.rules.append(rule)

    def diagnose(self, code: str, compiler_error: str = "", runtime_error: str = "") -> List[Dict[str, Any]]:
        """
        Diagnoses all active misconceptions present in the student submission.
        """
        combined_error = f"{compiler_error} {runtime_error}".strip()
        diagnosed = []

        for rule in self.rules:
            if rule.evaluate(code, combined_error):
                diagnosed.append({
                    "rule_code": rule.rule_code,
                    "name": rule.name,
                    "severity": rule.severity,
                    "explanation": rule.explanation,
                    "suggested_remedy": rule.suggested_remedy,
                })

        return diagnosed
