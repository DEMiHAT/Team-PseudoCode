"""
Structured Prompt Templates for IT22301 Data Structures and Algorithms Tutoring.
Enforces all pedagogical rules, cognitive scaffolding tiers, and anti-hallucination guardrails.
"""

import json
from typing import Optional, Dict, Any
from app.ai_tutor.schemas import TutorContext


SYSTEM_TEACHING_INSTRUCTION = """
You are an expert 1-to-1 computer science tutor for undergraduate engineering students enrolled in IT22301 - Data Structures and Algorithms.

STRICT PEDAGOGICAL RULES YOU MUST OBEY:
1. Student-Adaptive Framing: Explain concepts matched to the student's current mastery level (Novice, Developing, Competent, Mastered).
2. Primary Language: Use idiomatic Java code and standard collections (e.g. java.util.Stack, ArrayDeque, custom Node references).
3. Single Actionable Step: Provide strictly ONE clear, actionable hint or next step at a time. Do not overwhelm the student.
4. No Solution Spoilers: Do NOT provide the complete working solution unless the scaffolding level explicitly states Level 5 (Worked Solution). For levels 1-4, always stop before revealing the answer.
5. Scaffold Respect:
   - Level 1 (Conceptual): Ask Socratic reflective questions about data structure invariants; no direct code.
   - Level 2 (Targeted Hint): Highlight the specific edge-case or failure condition (e.g., empty stack pop, loop boundary).
   - Level 3 (Algorithm Guide): Provide high-level pseudocode or structured steps.
   - Level 4 (Partial Implementation): Provide a small Java code skeleton with missing blanks marked for the student.
   - Level 5 (Worked Solution): Provide a complete reference solution with line-by-line pedagogical annotations.
6. Execution Evidence Grounding:
   - Do NOT invent or hallucinate compiler or runtime errors.
   - Never declare student code "correct" or "bug-free" unless positive test execution evidence is explicitly provided.
   - Distinguish possible errors (hypotheses) from confirmed errors (supported by actual execution stdout/stderr).
7. Call to Action: Always conclude your response with a question or explicit instruction directing the student to attempt the next step.
8. Style: Direct, encouraging, academic, and free of extraneous emojis.
""".strip()


def build_hint_prompt(context: TutorContext) -> str:
    """Builds a prompt tailored to generate a scaffold-respecting hint."""
    scaffold_instructions = {
        0: "Level 0 (Independent): Encourage the student to analyze the problem independently. Do not provide code or algorithmic clues.",
        1: "Level 1 (Conceptual Prompt): Offer a high-level conceptual reflection question regarding the underlying LIFO/invariant behavior. Do not give any code.",
        2: "Level 2 (Targeted Hint): Identify the boundary condition or edge-case hazard (e.g., underflow, unbalanced closing brackets) without providing the fix.",
        3: "Level 3 (Algorithm Guidance): Outline the algorithmic flow or pseudocode logic step-by-step. Do not provide Java code.",
        4: "Level 4 (Partial Implementation): Provide a brief Java skeleton with a targeted comment indicating where the student must insert the guard or condition.",
        5: "Level 5 (Worked Solution): Provide the complete, clean Java solution accompanied by brief explanatory rationale.",
    }

    instruction = scaffold_instructions.get(context.scaffold_level, scaffold_instructions[1])

    mastery_summary = ", ".join(f"{k}: {v:.2f}" for k, v in context.estimated_mastery.items()) or "Initial baseline"
    previous_errs = "\n- ".join(context.previous_errors[-3:]) if context.previous_errors else "None recorded"
    previous_assists = "\n- ".join(context.previous_assistance[-2:]) if context.previous_assistance else "None"
    confirmed_misc = ", ".join(context.confirmed_misconceptions) if context.confirmed_misconceptions else "None confirmed"

    exec_info = "No execution output available."
    if context.execution_evidence.has_evidence:
        exec_info = f"Execution Status: {context.execution_evidence.status or 'Unknown'}\n"
        if context.execution_evidence.stderr:
            exec_info += f"Stderr/Errors: {context.execution_evidence.stderr}\n"
        if context.execution_evidence.stdout:
            exec_info += f"Stdout: {context.execution_evidence.stdout}\n"
        if context.execution_evidence.failed_test_case:
            exec_info += f"Failing Test Case: {json.dumps(context.execution_evidence.failed_test_case)}\n"

    return f"""
CURRICULAR CONTEXT:
- Course: {context.subject}
- Unit: {context.unit}
- Topic: {context.topic} (Subtopic: {context.subtopic or 'General'})

STUDENT PROFILE:
- Student ID: {context.student_id}
- Mastery Level: {context.mastery_level_label} (Scores: {mastery_summary})
- Confirmed Misconceptions: {confirmed_misc}
- Recent Errors:
- {previous_errs}
- Recent Scaffolding Given:
- {previous_assists}

STUDENT'S CURRENT JAVA CODE:
```java
{context.current_code or "// No code submitted yet"}
```

ACTUAL EXECUTION EVIDENCE:
{exec_info}

CURRENT PEDAGOGICAL DIRECTIVE:
Assistance Level: {context.scaffold_level}
Instruction: {instruction}

Remember:
- Give ONE actionable hint.
- Do not provide complete solution code unless Level 5 is specified.
- Conclude with an explicit prompt asking the student to take the next step.
""".strip()


def build_error_explanation_prompt(
    context: TutorContext,
    compiler_error: Optional[str] = None,
    runtime_error: Optional[str] = None,
    failed_test_details: Optional[Dict[str, Any]] = None,
) -> str:
    """Builds a prompt focused on deconstructing a specific compiler, runtime, or logical test failure."""
    raw_error_text = []
    if compiler_error and compiler_error.strip():
        raw_error_text.append(f"Compiler Error Output:\n{compiler_error.strip()}")
    if runtime_error and runtime_error.strip():
        raw_error_text.append(f"Runtime Exception:\n{runtime_error.strip()}")
    if failed_test_details:
        raw_error_text.append(f"Failed Test Assertion:\n{json.dumps(failed_test_details, indent=2)}")

    error_summary = "\n\n".join(raw_error_text) if raw_error_text else "Code produces unexpected output on boundary tests."

    return f"""
CURRICULAR TOPIC: {context.topic} ({context.subject})
STUDENT MASTERY: {context.mastery_level_label}

STUDENT'S JAVA CODE:
```java
{context.current_code}
```

ACTUAL VERIFIED ERROR EVIDENCE:
{error_summary}

TASK FOR TUTOR:
1. Pinpoint the exact line or logic block in the student's code responsible for this error.
2. Clearly explain WHY Java is reporting this error (or why the test assertion failed).
3. If it is an unconfirmed hypothesis, explicitly state it as a possibility to investigate rather than a verified fact.
4. Suggest ONE concrete debugging step or check the student can perform right now.
5. Do NOT rewrite the student's entire method or provide the full fix.
6. Ask the student to inspect the specific condition and make the change.
""".strip()


def build_concept_simplification_prompt(
    context: TutorContext,
    concept_name: str,
    student_question: Optional[str] = None,
    analogy_domain: str = "everyday physical systems",
) -> str:
    """Builds a prompt to explain and simplify an abstract DSA concept with concrete analogies."""
    question_context = f"Student's Specific Question: \"{student_question}\"" if student_question else "The student requested an intuitive explanation."

    return f"""
CURRICULAR TOPIC: {concept_name} (in {context.topic}, {context.subject})
STUDENT PROFICIENCY: {context.mastery_level_label}
{question_context}

TASK FOR TUTOR:
1. Explain '{concept_name}' using an intuitive analogy drawn from {analogy_domain}.
2. Relate the analogy back to the computer science data structure mechanics in Java (e.g. how memory or pointers change).
3. Include a very small, clean 3-5 line Java code snippet showing the minimal idiom.
4. Conclude with a quick check-for-understanding question asking the student how they would apply this concept.
""".strip()


def build_practice_question_prompt(
    context: TutorContext,
    target_concept: str,
    difficulty: str = "Intermediate",
    count: int = 1,
) -> str:
    """Builds a prompt requesting structured JSON practice questions for targeted skill remediation."""
    return f"""
You are creating a targeted formative assessment question for IT22301 (Data Structures and Algorithms).

TARGET CONCEPT: {target_concept}
TARGET DIFFICULTY: {difficulty}
STUDENT PROFICIENCY: {context.mastery_level_label}
CONFIRMED MISCONCEPTIONS TO TARGET: {', '.join(context.confirmed_misconceptions) or 'Boundary underflow checks'}

Generate exactly {count} multiple-choice question(s) formatted as strict JSON matching this schema:
[
  {{
    "question_id": "PQ-STACK-01",
    "prompt": "Clear problem statement describing a code snippet or data structure scenario in Java.",
    "sample_code_snippet": "Optional 2-6 lines of Java code, or null",
    "options": [
      {{"id": "A", "text": "First option"}},
      {{"id": "B", "text": "Second option"}},
      {{"id": "C", "text": "Third option"}},
      {{"id": "D", "text": "Fourth option"}}
    ],
    "correct_option_id": "B",
    "explanation": "Detailed explanation of why B is correct and why the other options represent typical misconceptions.",
    "target_skill": "{target_concept}",
    "difficulty": "{difficulty}"
  }}
]

RULES:
- Return ONLY valid JSON array. No markdown fences, no explanatory preamble.
- Options must be plausible, specifically designed to address common student slips (such as off-by-one or missing empty checks).
""".strip()

