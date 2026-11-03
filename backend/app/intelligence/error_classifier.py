"""
Practical Error Classification Module.
Categorizes student programming mistakes into a structured, explainable taxonomy.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ErrorCategory(str, Enum):
    """Taxonomy of practical programming and algorithmic errors."""
    COMPILATION = "compilation"                   # Java syntax, import, or type mismatch
    RUNTIME_EXCEPTION = "runtime_exception"       # General unhandled exceptions
    EMPTY_STACK_ACCESS = "empty_stack_access"     # EmptyStackException / underflow on pop/peek
    MATCHING_ORDER = "matching_order"             # Comparing mismatched bracket pairs or inverted order
    NESTED_BRACKET = "nested_bracket"             # Failing interleaved nesting (e.g., "([)]")
    EDGE_CASE = "edge_case"                       # Boundary failures (empty string, single bracket, odd length)
    INVARIANT_VIOLATION = "invariant_violation"   # Forgetting to verify stack.isEmpty() at end of traversal


class ErrorSeverity(str, Enum):
    """Severity weighting for cognitive intervention prioritization."""
    CRITICAL = "critical"   # Blocks execution completely (compilation, crash)
    MAJOR = "major"         # Core algorithmic logic failure (incorrect state transition)
    MINOR = "minor"         # Boundary or edge condition slip
    WARNING = "warning"     # Inefficient structure or redundant operation


class ClassifiedError(BaseModel):
    """Structured representation of an evaluated error signature."""
    category: ErrorCategory
    severity: ErrorSeverity
    title: str
    description: str
    evidence_snippet: Optional[str] = None
    affected_test_input: Optional[str] = None
    suggested_action: str
    is_recurrent: bool = False


class PracticalErrorClassifier:
    """
    Evaluates sandbox execution artifacts (compiler outputs, stderr, test inputs/outputs)
    and classifies practical coding errors with zero black-box assumptions.
    """

    @classmethod
    def classify_execution(
        cls,
        code: str,
        compile_output: Optional[str] = None,
        stderr: Optional[str] = None,
        test_failures: Optional[List[Dict[str, Any]]] = None,
    ) -> List[ClassifiedError]:
        """
        Analyzes compilation output, runtime exceptions, and failing test vectors
        to produce a prioritized list of classified errors.
        """
        classified: List[ClassifiedError] = []
        test_failures = test_failures or []

        # 1. Compilation Error Analysis
        if compile_output and compile_output.strip():
            classified.append(cls._classify_compilation_error(compile_output))

        # 2. Runtime Error Analysis (e.g. EmptyStackException)
        if stderr and stderr.strip():
            runtime_err = cls._classify_runtime_error(stderr)
            if runtime_err:
                classified.append(runtime_err)

        # 3. Test Vector Failure Analysis
        for fail in test_failures:
            inp = fail.get("input", "")
            exp = fail.get("expected", "")
            act = fail.get("actual", "")

            # Check for Empty Stack Access on Closing Bracket First
            if inp in ('"]"', '")"', '"}"', '"][)"') and (
                "EmptyStackException" in str(fail.get("error", "")) or "false" in exp and "true" not in act
            ):
                classified.append(
                    ClassifiedError(
                        category=ErrorCategory.EMPTY_STACK_ACCESS,
                        severity=ErrorSeverity.CRITICAL,
                        title="Empty Stack Access on Unmatched Closing Bracket",
                        description="Attempted to inspect or pop from an empty stack when the first character is a closing bracket.",
                        affected_test_input=inp,
                        suggested_action="Verify `!stack.isEmpty()` before calling `stack.pop()` or `stack.peek()`.",
                    )
                )

            # Check for Nested Bracket Misconception (e.g. "([)]")
            elif inp in ('"([)]"', '"[({})]"', '"[(])"') and exp == "false":
                classified.append(
                    ClassifiedError(
                        category=ErrorCategory.NESTED_BRACKET,
                        severity=ErrorSeverity.MAJOR,
                        title="Nested Bracket Ordering Violation",
                        description="Fails when bracket types interleave without proper LIFO nesting (e.g., '([)]').",
                        affected_test_input=inp,
                        suggested_action="Ensure the top of the stack matches the specific opening counterpart of the current closing bracket.",
                    )
                )

            # Check for Edge Cases (Empty string or Odd length)
            elif inp in ('""', '"[]"') or (len(inp.strip('"')) % 2 != 0 and exp == "false"):
                classified.append(
                    ClassifiedError(
                        category=ErrorCategory.EDGE_CASE,
                        severity=ErrorSeverity.MINOR,
                        title="Edge Case / Boundary Slip",
                        description="Fails on boundary inputs such as empty strings, single characters, or odd-length bracket strings.",
                        affected_test_input=inp,
                        suggested_action="A valid bracket sequence cannot have an odd length, and an empty sequence is vacuously valid.",
                    )
                )

            # Check for Invariant Violation (Unclosed opening brackets e.g. "(((")
            elif inp in ('"((("', '"["', '"{"', '"(()"') and exp == "false" and act == "true":
                classified.append(
                    ClassifiedError(
                        category=ErrorCategory.INVARIANT_VIOLATION,
                        severity=ErrorSeverity.MAJOR,
                        title="Unclosed Opening Brackets Invariant Failure",
                        description="Reported valid when open brackets remain unclosed on the stack at the end of input.",
                        affected_test_input=inp,
                        suggested_action="Return `stack.isEmpty()` at the conclusion of the iteration instead of returning `true`.",
                    )
                )

        return classified

    @classmethod
    def _classify_compilation_error(cls, compile_text: str) -> ClassifiedError:
        """Classifies compiler messages into readable diagnostics."""
        clean_text = compile_text[:300]
        if "cannot find symbol" in clean_text:
            return ClassifiedError(
                category=ErrorCategory.COMPILATION,
                severity=ErrorSeverity.CRITICAL,
                title="Unresolved Symbol or Missing Import",
                description="The compiler cannot locate class or method definition (e.g. `import java.util.Stack;`).",
                evidence_snippet=clean_text,
                suggested_action="Ensure `import java.util.Stack;` is present and class names match standard Java syntax.",
            )
        elif "incompatible types" in clean_text:
            return ClassifiedError(
                category=ErrorCategory.COMPILATION,
                severity=ErrorSeverity.CRITICAL,
                title="Generic Type Incompatibility",
                description="Type mismatch between primitives and wrapper types (e.g. `Stack<char>` instead of `Stack<Character>`).",
                evidence_snippet=clean_text,
                suggested_action="Use `Stack<Character>` rather than primitive `char` as generic type arguments.",
            )
        return ClassifiedError(
            category=ErrorCategory.COMPILATION,
            severity=ErrorSeverity.CRITICAL,
            title="Java Syntax or Structure Compilation Error",
            description="The Java compiler encountered invalid syntax or unmatched delimiters.",
            evidence_snippet=clean_text,
            suggested_action="Review line numbers indicated in compiler output to fix semicolons or braces.",
        )

    @classmethod
    def _classify_runtime_error(cls, stderr_text: str) -> Optional[ClassifiedError]:
        """Classifies runtime crash signatures."""
        if "EmptyStackException" in stderr_text:
            return ClassifiedError(
                category=ErrorCategory.EMPTY_STACK_ACCESS,
                severity=ErrorSeverity.CRITICAL,
                title="Java EmptyStackException",
                description="`pop()` or `peek()` was invoked when the stack contained no elements.",
                evidence_snippet="java.util.EmptyStackException",
                suggested_action="Guard every `pop()` operation with `if (stack.isEmpty()) return false;`.",
            )
        elif "NullPointerException" in stderr_text:
            return ClassifiedError(
                category=ErrorCategory.RUNTIME_EXCEPTION,
                severity=ErrorSeverity.CRITICAL,
                title="NullPointerException Dereference",
                description="Attempted to access members on an uninitialized reference.",
                evidence_snippet="java.lang.NullPointerException",
                suggested_action="Initialize objects before calling methods on them.",
            )
        return None


error_classifier = PracticalErrorClassifier()
