"""
LLM Tutor Model

Uses Google Gemini to generate personalized programming
explanations, hints, error guidance, and step-by-step help.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from google import genai


load_dotenv()


class TutorError(Exception):
    """Raised when the LLM Tutor cannot generate a response."""


@dataclass
class TutorResponse:
    response: str
    response_type: str
    model: str


class LLMTutor:

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        # Use the explicitly provided key, even if it is empty.
        # Read from .env only when api_key is None.
        if api_key is None:
            self.api_key = os.getenv("GEMINI_API_KEY")
        else:
            self.api_key = api_key

        if self.api_key:
            self.api_key = self.api_key.strip()
        else:
            self.api_key = None

        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        self.client = None

        # Initialize Gemini only when an API key is available.
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def _generate(
        self,
        prompt: str,
        response_type: str,
    ) -> TutorResponse:

        if not self.client:
            raise TutorError(
                "Gemini API key not configured. "
                "Set GEMINI_API_KEY in your environment."
            )

        try:
            result = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            answer = result.text

            if not answer or not answer.strip():
                raise TutorError(
                    "Gemini returned an empty response."
                )

            return TutorResponse(
                response=answer.strip(),
                response_type=response_type,
                model=self.model,
            )

        except TutorError:
            raise

        except Exception as exc:
            raise TutorError(
                f"Unable to generate tutor response: {exc}"
            ) from exc

    def generate_explanation(
        self,
        concept: str,
        mastery_percentage: float = 0.0,
    ) -> TutorResponse:

        self._validate_mastery(mastery_percentage)

        prompt = f"""
You are an intelligent programming tutor helping a student
learn Data Structures and Algorithms.

Concept: {concept}
Student mastery: {mastery_percentage}%

Instructions:
1. Explain the concept in simple beginner-friendly language.
2. Adapt the explanation to the student's mastery level.
3. Use a small practical example.
4. Explain the important steps clearly.
5. Avoid unnecessary advanced terminology.
6. Do not assume the student already understands the concept.

Do not simply provide a definition. Teach the concept.
"""

        return self._generate(prompt, "explanation")

    def generate_hint(
        self,
        question: str,
        student_code: str = "",
        error_context: str = "",
    ) -> TutorResponse:

        prompt = f"""
You are a patient programming tutor.

Student question:
{question}

Student code:
{student_code or "Not provided"}

Diagnosed error:
{error_context or "Not provided"}

Instructions:
1. Give one useful hint at a time.
2. Help the student think through the problem.
3. Point toward the relevant concept or operation.
4. Do not provide the complete solution.
5. Do not rewrite the entire program.
6. Use simple language.
"""

        return self._generate(prompt, "hint")

    def explain_error(
        self,
        code: str,
        error_category: str,
        error_details: str = "",
    ) -> TutorResponse:

        prompt = f"""
You are an expert programming tutor.

Student code:
{code or "Not provided"}

Diagnosed error category:
{error_category}

Error details:
{error_details or "No additional details provided"}

Instructions:
1. Explain what the error means.
2. Identify the likely reason it occurred.
3. Explain the underlying programming concept.
4. Show the student how to approach fixing it.
5. Include a small example if useful.
6. Do not shame or criticize the student.
7. Use beginner-friendly language.
"""

        return self._generate(prompt, "error_explanation")

    def generate_step_by_step(
        self,
        question: str,
        mastery_percentage: float = 0.0,
    ) -> TutorResponse:

        self._validate_mastery(mastery_percentage)

        prompt = f"""
You are an intelligent Data Structures and Algorithms tutor.

Student question:
{question}

Student mastery:
{mastery_percentage}%

Instructions:
1. Break the problem into small steps.
2. Explain the logic before the implementation.
3. Use a beginner-friendly example.
4. Explain important edge cases.
5. Use Java when showing programming code.
6. Explain the time and space complexity when relevant.
7. Encourage understanding instead of memorization.
"""

        return self._generate(prompt, "step_by_step")

    @staticmethod
    def _validate_mastery(mastery_percentage: float) -> None:

        if isinstance(mastery_percentage, bool) or not isinstance(
            mastery_percentage, (int, float)
        ):
            raise TypeError(
                "mastery_percentage must be a number"
            )

        if not 0 <= mastery_percentage <= 100:
            raise ValueError(
                "mastery_percentage must be between 0 and 100"
            )


# Shared tutor instance
llm_tutor = LLMTutor()