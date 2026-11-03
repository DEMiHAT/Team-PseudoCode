"""
Progressive Scaffolding Module.
Implements the 6-Level Cognitive Scaffolding Spectrum (L0 to L5).
Completely decoupled from external LLMs: delivers structured pedagogical assistance.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ScaffoldingLevel(int, Enum):
    """The 6 progressive cognitive scaffolding tiers."""
    L0_INDEPENDENT = 0      # Independent attempt (Zero assistance, validates unassisted mastery)
    L1_CONCEPTUAL_PROMPT = 1 # Conceptual prompt (High-level Socratic question & invariant reflection)
    L2_TARGETED_HINT = 2     # Targeted hint (Pinpoints error category or boundary condition without code)
    L3_ALGORITHM_GUIDE = 3   # Algorithm guidance (Pseudocode & step-by-step logic loop)
    L4_PARTIAL_IMPL = 4      # Partial implementation (Code skeleton with targeted blanks)
    L5_WORKED_SOLUTION = 5   # Worked solution (Complete reference code with line-by-line explanation)


class ScaffoldingPayload(BaseModel):
    """Delivered scaffolding content for a specific tier."""
    level: int = Field(..., ge=0, le=5)
    level_name: str
    pedagogical_intent: str
    prompt_text: str
    code_template: Optional[str] = None
    pseudocode: Optional[str] = None
    is_independent: bool = False


# Curated, Deterministic Scaffolding Templates for Stack & Parentheses Validation
STACK_PARENTHESES_SCAFFOLDS: Dict[ScaffoldingLevel, Dict[str, Any]] = {
    ScaffoldingLevel.L0_INDEPENDENT: {
        "level_name": "L0 - Independent Attempt",
        "intent": "Unassisted problem-solving to measure true independent latent mastery.",
        "prompt": "Solve the problem using your own algorithmic logic without hints. All test results will feed into your independent mastery metrics.",
        "code_template": None,
        "pseudocode": None,
        "is_independent": True,
    },
    ScaffoldingLevel.L1_CONCEPTUAL_PROMPT: {
        "level_name": "L1 - Conceptual Prompt",
        "intent": "Encourages reflection on core invariants and LIFO data structure properties.",
        "prompt": "Reflect on how brackets nest. What relationship must exist between the most recently opened bracket and the first closing bracket encountered? What property of a Stack data structure matches this behavior?",
        "code_template": None,
        "pseudocode": None,
        "is_independent": False,
    },
    ScaffoldingLevel.L2_TARGETED_HINT: {
        "level_name": "L2 - Targeted Hint",
        "intent": "Pinpoints the specific edge case or boundary condition without giving away code.",
        "prompt": "Consider two boundary hazards: 1) What happens if the very first character in the string is a closing bracket like ']'? 2) What should happen if the loop completes but opening brackets remain unclosed on the stack (e.g. '(((')?",
        "code_template": None,
        "pseudocode": None,
        "is_independent": False,
    },
    ScaffoldingLevel.L3_ALGORITHM_GUIDE: {
        "level_name": "L3 - Algorithm Guidance",
        "intent": "Presents structured algorithmic pseudocode describing the state transitions.",
        "prompt": "Follow this algorithmic blueprint:\n1. Initialize an empty stack of characters.\n2. Iterate through each character `c` in the string:\n   a. If `c` is '(', '{', or '[', push onto the stack.\n   b. Otherwise (`c` is closing):\n      - If stack is empty, return false immediately.\n      - Pop the top character `top`.\n      - If `top` does not match `c`'s opening pair, return false.\n3. After the loop, return true ONLY if the stack is completely empty.",
        "code_template": None,
        "pseudocode": (
            "function isValid(s):\n"
            "    stack = new Stack()\n"
            "    for each char c in s:\n"
            "        if c in ['(', '{', '[']:\n"
            "            stack.push(c)\n"
            "        else:\n"
            "            if stack.isEmpty(): return false\n"
            "            top = stack.pop()\n"
            "            if not matches(top, c): return false\n"
            "    return stack.isEmpty()\n"
        ),
        "is_independent": False,
    },
    ScaffoldingLevel.L4_PARTIAL_IMPL: {
        "level_name": "L4 - Partial Implementation",
        "intent": "Provides a scaffolded Java code skeleton with guided blanks for student completion.",
        "prompt": "Complete the missing logic inside the provided Java template, paying special attention to the empty stack check and terminal return value.",
        "code_template": (
            "import java.util.Stack;\n\n"
            "class Solution {\n"
            "    public boolean isValid(String s) {\n"
            "        Stack<Character> stack = new Stack<>();\n"
            "        \n"
            "        for (char c : s.toCharArray()) {\n"
            "            if (c == '(' || c == '{' || c == '[') {\n"
            "                stack.push(c);\n"
            "            } else {\n"
            "                // 1. Guard against empty stack underflow\n"
            "                if (stack.isEmpty()) {\n"
            "                    return false;\n"
            "                }\n"
            "                // 2. Pop and verify matching bracket pairs\n"
            "                char top = stack.pop();\n"
            "                if ((c == ')' && top != '(') ||\n"
            "                    (c == '}' && top != '{') ||\n"
            "                    (c == ']' && top != '[')) {\n"
            "                    return false;\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "        // 3. Return true only if no unclosed brackets remain\n"
            "        return stack.isEmpty();\n"
            "    }\n"
            "}\n"
        ),
        "pseudocode": None,
        "is_independent": False,
    },
    ScaffoldingLevel.L5_WORKED_SOLUTION: {
        "level_name": "L5 - Worked Solution",
        "intent": "Presents the complete reference solution with line-by-line pedagogical annotations.",
        "prompt": "Study this complete, production-grade reference implementation. Note how the O(N) time and O(N) space bounds are respected, with full guard clauses against underflow.",
        "code_template": (
            "import java.util.Stack;\n\n"
            "class Solution {\n"
            "    public boolean isValid(String s) {\n"
            "        // Quick edge-case optimization: odd-length strings cannot be balanced\n"
            "        if (s == null || s.length() % 2 != 0) {\n"
            "            return false;\n"
            "        }\n"
            "        \n"
            "        Stack<Character> stack = new Stack<>();\n"
            "        for (int i = 0; i < s.length(); i++) {\n"
            "            char c = s.charAt(i);\n"
            "            if (c == '(' || c == '{' || c == '[') {\n"
            "                stack.push(c);\n"
            "            } else {\n"
            "                // Underflow check: closing bracket with empty stack\n"
            "                if (stack.isEmpty()) return false;\n"
            "                char top = stack.pop();\n"
            "                if (c == ')' && top != '(') return false;\n"
            "                if (c == '}' && top != '{') return false;\n"
            "                if (c == ']' && top != '[') return false;\n"
            "            }\n"
            "        }\n"
            "        // If open brackets remain unclosed, string is invalid\n"
            "        return stack.isEmpty();\n"
            "    }\n"
            "}\n"
        ),
        "pseudocode": None,
        "is_independent": False,
    },
}


class ProgressiveScaffoldingEngine:
    """
    Coordinates delivery of the 6-Level Scaffolding Spectrum.
    Ensures that assistance is systematically progressive and calibrated to student need.
    """

    @classmethod
    def get_scaffolding(cls, level: ScaffoldingLevel) -> ScaffoldingPayload:
        """Retrieves verified scaffolding content for a specified level."""
        data = STACK_PARENTHESES_SCAFFOLDS.get(level, STACK_PARENTHESES_SCAFFOLDS[ScaffoldingLevel.L1_CONCEPTUAL_PROMPT])
        return ScaffoldingPayload(
            level=level.value,
            level_name=data["level_name"],
            pedagogical_intent=data["intent"],
            prompt_text=data["prompt"],
            code_template=data.get("code_template"),
            pseudocode=data.get("pseudocode"),
            is_independent=data.get("is_independent", False),
        )


scaffolding_engine = ProgressiveScaffoldingEngine()
