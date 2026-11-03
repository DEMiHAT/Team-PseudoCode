"""
Gemini Service Client.
Provides a resilient, decoupled interface for LLM-based Socratic tutoring.
Handles external API interaction gracefully with strict error boundaries and fallback awareness.
"""

from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class GeminiServiceClient:
    """Interface to Google Gemini API for personalized Socratic explanations."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def is_configured(self) -> bool:
        """Returns True if a non-empty API key is configured."""
        return bool(self.api_key and self.api_key.strip())

    async def check_health(self) -> Dict[str, Any]:
        """
        Verifies connectivity and validity of Gemini API configuration.
        """
        if not self.is_configured:
            return {
                "name": "Google Gemini API",
                "status": "unconfigured",
                "is_healthy": False,
                "endpoint": self.base_url,
                "message": "GEMINI_API_KEY is not set. System will utilize deterministic pedagogical fallbacks.",
            }

        try:
            url = f"{self.base_url}/{self.model}?key={self.api_key}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return {
                        "name": "Google Gemini API",
                        "status": "online",
                        "is_healthy": True,
                        "endpoint": self.base_url,
                        "message": f"Connected to {self.model} successfully.",
                    }
                else:
                    return {
                        "name": "Google Gemini API",
                        "status": "degraded",
                        "is_healthy": False,
                        "endpoint": self.base_url,
                        "message": f"API returned status {response.status_code}: {response.text[:100]}",
                    }
        except Exception as exc:
            logger.warning(f"Gemini API health check failed: {exc}")
            return {
                "name": "Google Gemini API",
                "status": "offline",
                "is_healthy": False,
                "endpoint": self.base_url,
                "message": f"Connection error: {str(exc)}",
            }

    async def generate_socratic_hint(
        self,
        problem_title: str,
        problem_description: str,
        student_code: str,
        scaffolding_tier: int,
        misconception_diagnosis: Optional[str] = None,
        error_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Requests targeted Socratic tutoring from Gemini without giving away the full solution.
        """
        if not self.is_configured:
            return {
                "success": False,
                "is_fallback": True,
                "reason": "API key unconfigured",
                "hint_text": None,
            }

        tier_instructions = {
            1: "Provide a subtle conceptual reminder. Do not mention code. Ask a guiding reflective question.",
            2: "Provide high-level algorithmic pseudocode or invariant logic. Point out where the logic diverges.",
            3: "Provide a concrete state trace showing how pointer or array values change on a failing input.",
            4: "Provide a minimal code skeleton with FIX-ME comments highlighting the exact bug.",
        }

        prompt = (
            f"You are a specialized 1-to-1 computer science tutor for undergraduate course IT22301 (Data Structures & Algorithms).\n"
            f"Problem: {problem_title}\n"
            f"Context: {problem_description[:300]}...\n\n"
            f"Student's Java Code:\n```java\n{student_code}\n```\n"
            f"Diagnosed Cognitive Slip: {misconception_diagnosis or 'Logic/Boundary discrepancy'}\n"
            f"Error / Output: {error_context or 'Fails edge case tests'}\n\n"
            f"Pedagogical Instruction (Tier {scaffolding_tier}): {tier_instructions.get(scaffolding_tier, tier_instructions[1])}\n"
            f"Keep your tone supportive, concise, academic, and non-prescriptive. Do not write the full solution."
        )

        try:
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 350,
                },
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    hint_text = (
                        data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                    )
                    return {
                        "success": True,
                        "is_fallback": False,
                        "hint_text": hint_text.strip(),
                    }
                else:
                    logger.error(f"Gemini generation error HTTP {res.status_code}: {res.text}")
                    return {
                        "success": False,
                        "is_fallback": True,
                        "reason": f"HTTP {res.status_code}",
                        "hint_text": None,
                    }
        except Exception as exc:
            logger.error(f"Failed to query Gemini API: {exc}")
            return {
                "success": False,
                "is_fallback": True,
                "reason": str(exc),
                "hint_text": None,
            }


# Singleton service instance
gemini_service = GeminiServiceClient()

