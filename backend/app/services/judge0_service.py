"""
Judge0 CE Code Execution Client.
Handles compilation, sandboxed execution, and test evaluation of Java code.
Operates via Judge0 REST API with transparent resilience when offline.
"""

from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger

# Judge0 Language ID for Java (OpenJDK)
JAVA_LANGUAGE_ID = 62


class Judge0ServiceClient:
    """Interface to Judge0 CE service for compiling and running Java DSA code."""

    def __init__(self):
        self.api_url = settings.JUDGE0_API_URL.rstrip("/")
        self.api_key = settings.JUDGE0_API_KEY
        self.api_host = settings.JUDGE0_API_HOST
        self.timeout = settings.JUDGE0_TIMEOUT_SECONDS

    def _get_headers(self) -> Dict[str, str]:
        """Constructs request headers, including RapidAPI headers if configured."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["X-RapidAPI-Key"] = self.api_key
        if self.api_host:
            headers["X-RapidAPI-Host"] = self.api_host
        return headers

    async def check_health(self) -> Dict[str, Any]:
        """Verifies if the Judge0 execution server is reachable."""
        try:
            url = f"{self.api_url}/about"
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(url, headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    version = data.get("version", "CE")
                    return {
                        "name": "Judge0 CE Execution Server",
                        "status": "online",
                        "is_healthy": True,
                        "endpoint": self.api_url,
                        "message": f"Judge0 {version} ready for Java code execution.",
                    }
                else:
                    return {
                        "name": "Judge0 CE Execution Server",
                        "status": "degraded",
                        "is_healthy": False,
                        "endpoint": self.api_url,
                        "message": f"Server responded with HTTP {res.status_code}.",
                    }
        except Exception as exc:
            return {
                "name": "Judge0 CE Execution Server",
                "status": "offline",
                "is_healthy": False,
                "endpoint": self.api_url,
                "message": (
                    f"Unreachable at {self.api_url}. "
                    "Ensure Judge0 Docker container is active or update JUDGE0_API_URL in .env."
                ),
            }

    async def execute_java_code(
        self,
        source_code: str,
        stdin_input: str = "",
        expected_output: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submits Java code to Judge0 CE for synchronous execution.
        """
        health = await self.check_health()
        if not health["is_healthy"]:
            # Provide an honest, structured execution failure detailing server offline state
            return {
                "status": "Execution Server Offline",
                "is_passed": False,
                "stdout": None,
                "stderr": None,
                "compile_output": (
                    f"Judge0 CE server is currently offline at {self.api_url}. "
                    "Please launch Judge0 CE via Docker or configure an active instance in backend/.env."
                ),
                "execution_time_ms": 0.0,
                "memory_kb": 0.0,
                "is_service_available": False,
            }

        url = f"{self.api_url}/submissions?base64_encoded=false&wait=true"
        payload = {
            "source_code": source_code,
            "language_id": JAVA_LANGUAGE_ID,
            "stdin": stdin_input,
            "expected_output": expected_output,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self._get_headers())
                if response.status_code in (200, 201):
                    result = response.json()
                    status_info = result.get("status", {})
                    status_desc = status_info.get("description", "Unknown")

                    stdout = result.get("stdout") or ""
                    stderr = result.get("stderr") or ""
                    compile_output = result.get("compile_output") or ""
                    time_taken = float(result.get("time") or 0.0) * 1000.0
                    memory = float(result.get("memory") or 0.0)

                    # Status 3 in Judge0 indicates Accepted
                    is_passed = status_info.get("id") == 3
                    if not is_passed and expected_output is not None:
                        is_passed = stdout.strip() == expected_output.strip()

                    return {
                        "status": status_desc,
                        "is_passed": is_passed,
                        "stdout": stdout,
                        "stderr": stderr,
                        "compile_output": compile_output,
                        "execution_time_ms": time_taken,
                        "memory_kb": memory,
                        "is_service_available": True,
                    }
                else:
                    return {
                        "status": "Submission Failed",
                        "is_passed": False,
                        "stdout": None,
                        "stderr": response.text,
                        "compile_output": f"HTTP {response.status_code} from execution server.",
                        "execution_time_ms": 0.0,
                        "memory_kb": 0.0,
                        "is_service_available": False,
                    }
        except Exception as exc:
            logger.error(f"Error executing code on Judge0: {exc}")
            return {
                "status": "Execution Error",
                "is_passed": False,
                "stdout": None,
                "stderr": str(exc),
                "compile_output": f"Failed to execute code: {str(exc)}",
                "execution_time_ms": 0.0,
                "memory_kb": 0.0,
                "is_service_available": False,
            }


# Singleton service instance
judge0_service = Judge0ServiceClient()

