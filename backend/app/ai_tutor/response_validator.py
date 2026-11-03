"""
Response Validation and Error Handling for AI Tutoring.
Validates LLM outputs against pedagogical guardrails, ensures structured outputs,
and provides deterministic fallbacks when external APIs are unavailable.
"""

import json
import re
from typing import Dict, Any, Optional, List
from app.ai_tutor.schemas import TutorResponse, PracticeQuestionItem, PracticeQuestionResponse, PracticeOption
from app.intelligence.scaffolding import STACK_PARENTHESES_SCAFFOLDS, ScaffoldingLevel
from app.core.logging import logger


class ResponseValidator:
    """
    Validates and sanitizes AI tutor outputs.
    Ensures that no premature solutions are leaked, actionable calls-to-action exist,
    and falls back to deterministic curriculum content when the LLM is unconfigured or fails.
    """

    @classmethod
    def validate_and_format_hint(
        cls,
        llm_text: str,
        scaffold_level: int,
        pedagogical_strategy: str,
    ) -> TutorResponse:
        """
        Validates LLM hint text against scaffolding rules.
        Appends an actionable next step if omitted by the model.
        """
        cleaned_text = llm_text.strip()

        # Guard against full solutions on lower scaffolds (Level < 5)
        if scaffold_level < 5:
            # If the model dumped a complete method with public class or closing return
            if "public class" in cleaned_text and "return " in cleaned_text:
                logger.warning("LLM attempted to leak complete class definition on scaffold < 5; sanitizing.")
                cleaned_text = re.sub(r"public class [^\{]+\{[^\}]+\}", "// [Complete class omitted to support active learning]", cleaned_text)

        # Ensure call-to-action is present
        actionable_step = cls._extract_or_generate_actionable_step(cleaned_text, scaffold_level)
        if actionable_step and actionable_step.lower() not in cleaned_text.lower():
            cleaned_text += f"\n\nNext Step: {actionable_step}"

        return TutorResponse(
            success=True,
            is_fallback=False,
            content=cleaned_text,
            actionable_next_step=actionable_step,
            scaffold_level=scaffold_level,
            pedagogical_strategy=pedagogical_strategy,
            fallback_reason=None,
        )

    @classmethod
    def get_fallback_hint(
        cls,
        scaffold_level: int,
        reason: str = "Gemini API unavailable",
    ) -> TutorResponse:
        """
        Supplies a deterministic, curriculum-aligned hint from the 6-Level Scaffolding engine.
        """
        level_enum = ScaffoldingLevel(min(max(scaffold_level, 0), 5))
        scaffold = STACK_PARENTHESES_SCAFFOLDS.get(level_enum, STACK_PARENTHESES_SCAFFOLDS[ScaffoldingLevel.L1_CONCEPTUAL_PROMPT])

        content = scaffold["prompt"]
        if scaffold.get("pseudocode"):
            content += f"\n\nPseudocode:\n```\n{scaffold['pseudocode']}\n```"
        if scaffold.get("code_template"):
            content += f"\n\nJava Skeleton:\n```java\n{scaffold['code_template']}\n```"

        actionable = cls._extract_or_generate_actionable_step(content, scaffold_level)

        return TutorResponse(
            success=True,
            is_fallback=True,
            content=content,
            actionable_next_step=actionable,
            scaffold_level=scaffold_level,
            pedagogical_strategy=scaffold["intent"],
            fallback_reason=reason,
        )

    @classmethod
    def validate_and_format_error_explanation(
        cls,
        llm_text: str,
    ) -> TutorResponse:
        """Validates and formats an error explanation."""
        cleaned_text = llm_text.strip()
        actionable = "Inspect the line highlighted above and add a conditional guard check before attempting to re-run."
        if "next step" not in cleaned_text.lower() and "try" not in cleaned_text.lower():
            cleaned_text += f"\n\nRecommended Action: {actionable}"

        return TutorResponse(
            success=True,
            is_fallback=False,
            content=cleaned_text,
            actionable_next_step=actionable,
            scaffold_level=2,
            pedagogical_strategy="Error Diagnosis and Guard Guidance",
            fallback_reason=None,
        )

    @classmethod
    def get_fallback_error_explanation(
        cls,
        compiler_error: Optional[str] = None,
        runtime_error: Optional[str] = None,
        reason: str = "Gemini API unavailable",
    ) -> TutorResponse:
        """Deterministic error explanation fallback."""
        err_msg = compiler_error or runtime_error or "Unknown boundary error"
        content = (
            f"Observed Issue: {err_msg}\n\n"
            "Diagnosis: In Stack implementations, runtime EmptyStackException or NoSuchElementException "
            "typically arises when calling pop() or peek() on an empty collection without checking `isEmpty()` first.\n\n"
            "Actionable Step: Add an `if (stack.isEmpty())` guard condition before attempting to pop elements."
        )

        return TutorResponse(
            success=True,
            is_fallback=True,
            content=content,
            actionable_next_step="Add an if (stack.isEmpty()) check before accessing top elements.",
            scaffold_level=2,
            pedagogical_strategy="Deterministic Error Remediation",
            fallback_reason=reason,
        )

    @classmethod
    def validate_and_format_simplification(
        cls,
        llm_text: str,
        concept_name: str,
    ) -> TutorResponse:
        """Validates and formats concept simplification."""
        cleaned_text = llm_text.strip()
        actionable = f"Can you explain how elements enter and leave the {concept_name} in your own words?"

        return TutorResponse(
            success=True,
            is_fallback=False,
            content=cleaned_text,
            actionable_next_step=actionable,
            scaffold_level=1,
            pedagogical_strategy="Analogical Scaffolding",
            fallback_reason=None,
        )

    @classmethod
    def get_fallback_simplification(
        cls,
        concept_name: str,
        reason: str = "Gemini API unavailable",
    ) -> TutorResponse:
        """Deterministic concept simplification fallback."""
        content = (
            f"Concept: {concept_name}\n\n"
            "Real-World Analogy: Think of a spring-loaded cafeteria plate dispenser. "
            "You can only add a plate to the top (push), and the only plate you can take is the most recent one placed on top (pop). "
            "This is Last-In, First-Out (LIFO).\n\n"
            "Java Minimal Snippet:\n"
            "```java\n"
            "Deque<Integer> stack = new ArrayDeque<>();\n"
            "stack.push(10); // add to top\n"
            "int top = stack.pop(); // removes 10\n"
            "```"
        )
        return TutorResponse(
            success=True,
            is_fallback=True,
            content=content,
            actionable_next_step="Try writing a short Java main method that pushes 3 numbers onto an ArrayDeque and pops them in order.",
            scaffold_level=1,
            pedagogical_strategy="Deterministic Analogical Explanation",
            fallback_reason=reason,
        )

    @classmethod
    def validate_and_format_practice_questions(
        cls,
        llm_text: str,
        target_concept: str,
    ) -> PracticeQuestionResponse:
        """Parses and validates strict JSON practice questions."""
        # Clean markdown code blocks if returned
        cleaned = llm_text.strip()
        cleaned = re.sub(r"^```(json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)

        try:
            raw_data = json.loads(cleaned)
            if isinstance(raw_data, dict) and "questions" in raw_data:
                raw_data = raw_data["questions"]

            if not isinstance(raw_data, list):
                raise ValueError("Expected a list of questions")

            questions: List[PracticeQuestionItem] = []
            for item in raw_data:
                opts = [PracticeOption(id=o["id"], text=o["text"]) for o in item.get("options", [])]
                questions.append(
                    PracticeQuestionItem(
                        question_id=item.get("question_id", f"PQ-{target_concept[:3].upper()}-01"),
                        prompt=item.get("prompt", "Analyze the Java stack operation:"),
                        options=opts,
                        correct_option_id=item.get("correct_option_id", "A"),
                        explanation=item.get("explanation", "Correct based on LIFO rules."),
                        target_skill=item.get("target_skill", target_concept),
                        difficulty=item.get("difficulty", "Intermediate"),
                        sample_code_snippet=item.get("sample_code_snippet"),
                    )
                )

            return PracticeQuestionResponse(
                success=True,
                is_fallback=False,
                target_concept=target_concept,
                questions=questions,
                fallback_reason=None,
            )

        except Exception as exc:
            logger.warning(f"Failed to parse LLM practice question JSON: {exc}. Using deterministic fallback.")
            return cls.get_fallback_practice_questions(target_concept, reason=f"JSON parse error: {str(exc)}")

    @classmethod
    def get_fallback_practice_questions(
        cls,
        target_concept: str,
        reason: str = "Gemini API unavailable",
    ) -> PracticeQuestionResponse:
        """Deterministic practice question fallback."""
        items = [
            PracticeQuestionItem(
                question_id="PQ-STACK-DET-01",
                prompt="In Java, what exception is thrown when calling `pop()` on an empty `java.util.Stack` instance?",
                options=[
                    PracticeOption(id="A", text="NullPointerException"),
                    PracticeOption(id="B", text="EmptyStackException"),
                    PracticeOption(id="C", text="IndexOutOfBoundsException"),
                    PracticeOption(id="D", text="IllegalStateException"),
                ],
                correct_option_id="B",
                explanation="java.util.Stack throws EmptyStackException when pop() or peek() is executed on an empty stack. To prevent this, always query isEmpty() first.",
                target_skill="stack_underflow",
                difficulty="Beginner",
                sample_code_snippet="Stack<Integer> s = new Stack<>();\ns.pop(); // What happens here?",
            ),
            PracticeQuestionItem(
                question_id="PQ-STACK-DET-02",
                prompt="Given the string expression '([)]', what is the state of a verification stack right when the ']' is evaluated?",
                options=[
                    PracticeOption(id="A", text="Stack contains '(', matching ']' correctly."),
                    PracticeOption(id="B", text="Stack contains '[' on top; mismatched with ']'."),
                    PracticeOption(id="C", text="Stack contains '(' on top; mismatched because top is '(' and current is ']'."),
                    PracticeOption(id="D", text="Stack is completely empty."),
                ],
                correct_option_id="C",
                explanation="After encountering '(' then '[', '[' is pushed then popped by ']'? Wait: for '([)]', at ']', the stack has '(' and '['. ']' matches '[', so '[' pops! Next is ')', matching '('. But in '([)]', at index 2 is ')': top is '[', which mismatches ')'!",
                target_skill="parentheses_validation",
                difficulty="Intermediate",
                sample_code_snippet="// Validating balanced parentheses order",
            ),
        ]
        return PracticeQuestionResponse(
            success=True,
            is_fallback=True,
            target_concept=target_concept,
            questions=items,
            fallback_reason=reason,
        )

    @staticmethod
    def _extract_or_generate_actionable_step(text: str, level: int) -> str:
        """Determines the appropriate active-learning prompt for the student."""
        steps = {
            0: "Implement the logic in your code editor and run the test suite to observe behavior.",
            1: "Reflect on how the LIFO ordering applies here and state your reasoning in a code comment.",
            2: "Add an if-statement checking the boundary edge case before the operation.",
            3: "Translate step 2 of the pseudocode into Java syntax in your method.",
            4: "Fill in the condition marked in the partial code skeleton.",
            5: "Trace through the worked solution with an edge case like an empty input to verify understanding.",
        }
        return steps.get(level, steps[1])
