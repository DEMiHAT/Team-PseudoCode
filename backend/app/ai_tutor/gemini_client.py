"""
Google Gemini API Client for Intelligent DSA Tutoring.
Provides secure, server-side communication with Google Gemini API models.
Handles timeouts, rate limits, network partitions, and unconfigured states gracefully.
"""

import json
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class GeminiClientError(Exception):
    """Base exception for Gemini client operations."""
    pass


class GeminiUnconfiguredError(GeminiClientError):
    """Raised when an operation requires an API key but none is configured."""
    pass


class GeminiClient:
    """
    Asynchronous client interface to Google Gemini models (e.g. gemini-1.5-flash).
    Credentials are read securely from server configuration and never transmitted to the frontend.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta/models",
        timeout_seconds: float = 12.0,
    ):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model_name = model_name if model_name is not None else settings.GEMINI_MODEL
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    @property
    def is_configured(self) -> bool:
        """Determines if a non-empty API key is present."""
        return bool(self.api_key and self.api_key.strip())

    async def check_health(self) -> Dict[str, Any]:
        """
        Queries model status without consuming generation tokens.
        Returns a diagnostic dictionary.
        """
        if not self.is_configured:
            return {
                "name": "Google Gemini API",
                "status": "unconfigured",
                "is_healthy": False,
                "endpoint": self.base_url,
                "model": self.model_name,
                "message": "GEMINI_API_KEY environment variable is unset or empty. Tutoring operates in deterministic fallback mode.",
            }

        url = f"{self.base_url}/{self.model_name}?key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    return {
                        "name": "Google Gemini API",
                        "status": "online",
                        "is_healthy": True,
                        "endpoint": self.base_url,
                        "model": self.model_name,
                        "message": f"Successfully connected to Gemini model {self.model_name}.",
                    }
                elif res.status_code == 400:
                    return {
                        "name": "Google Gemini API",
                        "status": "invalid_credentials",
                        "is_healthy": False,
                        "endpoint": self.base_url,
                        "model": self.model_name,
                        "message": "Invalid API key or project permission.",
                    }
                else:
                    return {
                        "name": "Google Gemini API",
                        "status": "degraded",
                        "is_healthy": False,
                        "endpoint": self.base_url,
                        "model": self.model_name,
                        "message": f"Gemini API returned HTTP {res.status_code}: {res.text[:120]}",
                    }
        except httpx.RequestError as exc:
            logger.warning(f"Gemini API health check connection failed: {exc}")
            return {
                "name": "Google Gemini API",
                "status": "offline",
                "is_healthy": False,
                "endpoint": self.base_url,
                "model": self.model_name,
                "message": f"Network transport error: {str(exc)}",
            }

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 600,
        response_mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches a structured generation request to Gemini.
        Returns a standardized payload:
        {
            "success": bool,
            "text": str,
            "raw_response": dict,
            "error": Optional[str],
            "is_unconfigured": bool
        }
        """
        if not self.is_configured:
            return {
                "success": False,
                "text": "",
                "raw_response": None,
                "error": "Gemini API key is not configured.",
                "is_unconfigured": True,
            }

        endpoint_url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        if response_mime_type:
            payload["generationConfig"]["responseMimeType"] = response_mime_type

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(endpoint_url, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        text_output = "".join(part.get("text", "") for part in parts)
                        return {
                            "success": True,
                            "text": text_output.strip(),
                            "raw_response": data,
                            "error": None,
                            "is_unconfigured": False,
                        }
                    else:
                        finish_reason = candidates[0].get("finishReason", "UNKNOWN") if candidates else "NO_CANDIDATES"
                        return {
                            "success": False,
                            "text": "",
                            "raw_response": data,
                            "error": f"Response generated no text content (finish reason: {finish_reason}).",
                            "is_unconfigured": False,
                        }

                elif response.status_code == 429:
                    logger.warning("Gemini API rate limit (HTTP 429) encountered.")
                    return {
                        "success": False,
                        "text": "",
                        "raw_response": None,
                        "error": "Gemini API rate limit exceeded.",
                        "is_unconfigured": False,
                    }

                elif response.status_code in (401, 403):
                    logger.error(f"Gemini API authentication rejected: HTTP {response.status_code}")
                    return {
                        "success": False,
                        "text": "",
                        "raw_response": None,
                        "error": f"Gemini API authorization failure (HTTP {response.status_code}).",
                        "is_unconfigured": False,
                    }

                else:
                    logger.error(f"Gemini API HTTP {response.status_code}: {response.text[:200]}")
                    return {
                        "success": False,
                        "text": "",
                        "raw_response": None,
                        "error": f"Gemini API returned error HTTP {response.status_code}.",
                        "is_unconfigured": False,
                    }

        except httpx.TimeoutException:
            logger.warning(f"Gemini API request timed out after {self.timeout_seconds}s.")
            return {
                "success": False,
                "text": "",
                "raw_response": None,
                "error": f"Gemini API request timed out after {self.timeout_seconds} seconds.",
                "is_unconfigured": False,
            }
        except httpx.RequestError as exc:
            logger.error(f"Gemini API network connection failure: {exc}")
            return {
                "success": False,
                "text": "",
                "raw_response": None,
                "error": f"Network transport error: {str(exc)}",
                "is_unconfigured": False,
            }
        except Exception as exc:
            logger.error(f"Unexpected error querying Gemini API: {exc}")
            return {
                "success": False,
                "text": "",
                "raw_response": None,
                "error": f"Internal exception: {str(exc)}",
                "is_unconfigured": False,
            }


# Default singleton client instance
gemini_client = GeminiClient()
