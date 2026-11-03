"""
Programming Error Diagnosis
Model 2 - Adaptive DSA Learning System

Purpose:
Identify common Java programming errors and DSA misconceptions
using rule-based diagnostic patterns.

This module does not compile or execute Java code.
It analyses compiler output, runtime output and test failures
provided by an external code execution system.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------
# 1. ERROR CATEGORIES
# ---------------------------------------------------------

class ErrorCategory(str, Enum):
    COMPILATION = "compilation_error"
    STACK_UNDERFLOW = "stack_underflow"
    STACK_OVERFLOW = "stack_overflow"
    LIFO_MISCONCEPTION = "lifo_misconception"
    PARENTHESES_VALIDATION = "parentheses_validation"
    NULL_POINTER = "null_pointer_error"
    ARRAY_INDEX = "array_index_error"
    LOGICAL = "logical_error"
    UNKNOWN = "unknown_error"


# ---------------------------------------------------------
# 2. SEVERITY LEVELS
# ---------------------------------------------------------

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ---------------------------------------------------------
# 3. DIAGNOSTIC RESULT
# ---------------------------------------------------------

@dataclass
class DiagnosticResult:
    category: ErrorCategory
    severity: Severity
    title: str
    explanation: str
    evidence: str
    suggested_action: str
    confidence: float
    misconception: bool = False


# ---------------------------------------------------------
# 4. ERROR DIAGNOSIS ENGINE
# ---------------------------------------------------------

class ProgrammingErrorDiagnoser:
    """
    Rule-based diagnostic engine for Java DSA programs.

    Input:
        code:
            Student's Java source code.

        compile_output:
            Compiler error messages, if any.

        runtime_output:
            Runtime error messages, if any.

        test_failures:
            Descriptions of failed test cases.

    Output:
        A list of structured diagnostic results.
    """

    def diagnose(
        self,
        code: str = "",
        compile_output: str = "",
        runtime_output: str = "",
        test_failures: Optional[List[str]] = None
    ) -> List[DiagnosticResult]:

        if not all(
            isinstance(value, str)
            for value in (code, compile_output, runtime_output)
        ):
            raise TypeError("Code and output values must be strings")

        if test_failures is not None:
            if not isinstance(test_failures, list):
                raise TypeError("test_failures must be a list")

            if not all(isinstance(item, str) for item in test_failures):
                raise TypeError("Every test failure must be a string")

        failures = test_failures or []

        combined_output = "\n".join(
            [compile_output, runtime_output] + failures
        )

        results = []

        # Run each independent diagnostic rule.
        self._check_compilation(compile_output, results)
        self._check_stack_underflow(combined_output, results)
        self._check_stack_overflow(combined_output, results)
        self._check_lifo_misconception(combined_output, results)
        self._check_parentheses(combined_output, results)
        self._check_null_pointer(combined_output, results)
        self._check_array_index(combined_output, results)
        self._check_logical_errors(failures, results)

        if not results:
            results.append(
                DiagnosticResult(
                    category=ErrorCategory.UNKNOWN,
                    severity=Severity.LOW,
                    title="No known error pattern identified",
                    explanation=(
                        "The supplied information does not match "
                        "any currently supported diagnostic rule."
                    ),
                    evidence="No matching diagnostic evidence.",
                    suggested_action=(
                        "Review the program output and failed test cases."
                    ),
                    confidence=0.0
                )
            )

        return results

    # -----------------------------------------------------
    # 5. COMPILATION ERROR DETECTION
    # -----------------------------------------------------

    def _check_compilation(self, output, results):

        if not output.strip():
            return

        results.append(
            DiagnosticResult(
                category=ErrorCategory.COMPILATION,
                severity=Severity.HIGH,
                title="Java compilation error",
                explanation=(
                    "The Java compiler reported an error. "
                    "The program may contain invalid syntax, "
                    "undefined symbols or incompatible types."
                ),
                evidence=output.strip(),
                suggested_action=(
                    "Read the compiler message and inspect the "
                    "reported line and column."
                ),
                confidence=0.99
            )
        )

    # -----------------------------------------------------
    # 6. STACK UNDERFLOW DETECTION
    # -----------------------------------------------------

    def _check_stack_underflow(self, text, results):

        patterns = [
            r"EmptyStackException",
            r"stack underflow",
            r"pop\s+from\s+empty\s+stack",
            r"peek\s+from\s+empty\s+stack",
            r"empty\s+stack\s+(?:exception|error)"
        ]

        if self._matches(patterns, text):

            results.append(
                DiagnosticResult(
                    category=ErrorCategory.STACK_UNDERFLOW,
                    severity=Severity.HIGH,
                    title="Stack underflow detected",
                    explanation=(
                        "The program attempted to remove or access "
                        "an element when the stack was empty."
                    ),
                    evidence=self._find_evidence(patterns, text),
                    suggested_action=(
                        "Check whether the stack is empty before "
                        "performing pop() or peek()."
                    ),
                    confidence=0.98,
                    misconception=True
                )
            )

    # -----------------------------------------------------
    # 7. STACK OVERFLOW DETECTION
    # -----------------------------------------------------

    def _check_stack_overflow(self, text, results):

        patterns = [
            r"stack overflow",
            r"stackoverflowerror",
            r"stack is full",
            r"stack capacity exceeded",
            r"push\s+to\s+full\s+stack"
        ]

        if self._matches(patterns, text):

            results.append(
                DiagnosticResult(
                    category=ErrorCategory.STACK_OVERFLOW,
                    severity=Severity.HIGH,
                    title="Stack overflow or capacity exceeded",
                    explanation=(
                        "The supplied error information indicates "
                        "that the stack capacity may have been exceeded "
                        "or recursive execution exhausted the call stack."
                    ),
                    evidence=self._find_evidence(patterns, text),
                    suggested_action=(
                        "Check stack capacity and push conditions. "
                        "If StackOverflowError occurred, inspect "
                        "recursive calls for missing termination."
                    ),
                    confidence=0.95
                )
            )

    # -----------------------------------------------------
    # 8. LIFO MISCONCEPTION DETECTION
    # -----------------------------------------------------

    def _check_lifo_misconception(self, text, results):

        patterns = [
            r"fifo\s+instead\s+of\s+lifo",
            r"lifo\s+order",
            r"last.in.first.out",
            r"oldest\s+element\s+removed",
            r"newest\s+element\s+expected",
            r"expected.*(?:last|top).*but\s+got",
            r"queue\s+behavior\s+instead\s+of\s+stack"
        ]

        if self._matches(patterns, text):

            results.append(
                DiagnosticResult(
                    category=ErrorCategory.LIFO_MISCONCEPTION,
                    severity=Severity.MEDIUM,
                    title="Possible LIFO misconception",
                    explanation=(
                        "The supplied test information suggests "
                        "that the student may not be following "
                        "Last In, First Out stack behaviour."
                    ),
                    evidence=self._find_evidence(patterns, text),
                    suggested_action=(
                        "Review push() and pop() operations. "
                        "The most recently inserted element "
                        "must be removed first."
                    ),
                    confidence=0.90,
                    misconception=True
                )
            )

    # -----------------------------------------------------
    # 9. PARENTHESES VALIDATION DETECTION
    # -----------------------------------------------------

    def _check_parentheses(self, text, results):

        patterns = [
            r"unbalanced\s+parentheses",
            r"unmatched\s+(?:opening|closing)\s+(?:bracket|parenthes\w*)",
            r"mismatched\s+brackets",
            r"unbalanced\s+brackets",
            r"brackets?\s+do\s+not\s+match",
            r"parentheses\s+do\s+not\s+match"
        ]

        if self._matches(patterns, text):

            results.append(
                DiagnosticResult(
                    category=ErrorCategory.PARENTHESES_VALIDATION,
                    severity=Severity.MEDIUM,
                    title="Parentheses validation error",
                    explanation=(
                        "The supplied test information indicates "
                        "that opening and closing brackets may "
                        "not be correctly matched."
                    ),
                    evidence=self._find_evidence(patterns, text),
                    suggested_action=(
                        "Check bracket types and use a stack to "
                        "match every opening bracket with its "
                        "corresponding closing bracket."
                    ),
                    confidence=0.95,
                    misconception=True
                )
            )

    # -----------------------------------------------------
    # 10. NULL POINTER DETECTION
    # -----------------------------------------------------

    def _check_null_pointer(self, text, results):

        patterns = [
            r"NullPointerException",
            r"cannot invoke.*because.*null",
            r"null reference"
        ]

        if self._matches(patterns, text):

            results.append(
                DiagnosticResult(
                    category=ErrorCategory.NULL_POINTER,
                    severity=Severity.HIGH,
                    title="Null pointer error",
                    explanation=(
                        "The program attempted to access a member "
                        "through a null reference."
                    ),
                    evidence=self._find_evidence(patterns, text),
                    suggested_action=(
                        "Check whether the object is initialized "
                        "before accessing its fields or methods."
                    ),
                    confidence=0.98
                )
            )

    # -----------------------------------------------------
    # 11. ARRAY INDEX DETECTION
    # -----------------------------------------------------

    def _check_array_index(self, text, results):

        patterns = [
            r"ArrayIndexOutOfBoundsException",
            r"IndexOutOfBoundsException",
            r"index.*out of bounds",
            r"array index.*out of range"
        ]

        if self._matches(patterns, text):

            results.append(
                DiagnosticResult(
                    category=ErrorCategory.ARRAY_INDEX,
                    severity=Severity.HIGH,
                    title="Array index out of bounds",
                    explanation=(
                        "The program attempted to access an "
                        "array or collection using an invalid index."
                    ),
                    evidence=self._find_evidence(patterns, text),
                    suggested_action=(
                        "Check index boundaries and ensure the "
                        "index is within the valid range."
                    ),
                    confidence=0.98
                )
            )

    # -----------------------------------------------------
    # 12. LOGICAL ERROR DETECTION
    # -----------------------------------------------------

    def _check_logical_errors(self, failures, results):

        if not failures:
            return

        # Avoid duplicating errors already classified by a
        # more specific diagnostic rule.
        known_patterns = [
            r"EmptyStackException",
            r"stack underflow",
            r"stack overflow",
            r"StackOverflowError",
            r"NullPointerException",
            r"ArrayIndexOutOfBoundsException",
            r"IndexOutOfBoundsException",
            r"unbalanced parentheses",
            r"unmatched .* bracket",
            r"mismatched brackets",
            r"lifo",
            r"fifo"
        ]

        unclassified_failures = [
            failure for failure in failures
            if not self._matches(known_patterns, failure)
        ]

        if unclassified_failures:

            results.append(
                DiagnosticResult(
                    category=ErrorCategory.LOGICAL,
                    severity=Severity.MEDIUM,
                    title="Possible logical error",
                    explanation=(
                        "One or more test cases failed. "
                        "The program may not be producing "
                        "the expected result."
                    ),
                    evidence="; ".join(unclassified_failures),
                    suggested_action=(
                        "Compare expected and actual outputs. "
                        "Review conditions, loops, indexes "
                        "and data structure operations."
                    ),
                    confidence=0.65
                )
            )

    # -----------------------------------------------------
    # 13. COMMON PATTERN UTILITIES
    # -----------------------------------------------------

    @staticmethod
    def _matches(patterns, text):

        return any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in patterns
        )

    @staticmethod
    def _find_evidence(patterns, text):

        for line in text.splitlines():

            if ProgrammingErrorDiagnoser._matches(
                patterns,
                line
            ):
                return line.strip()

        return text.strip()


# ---------------------------------------------------------
# 14. DEFAULT DIAGNOSER INSTANCE
# ---------------------------------------------------------

error_diagnoser = ProgrammingErrorDiagnoser()