"""
Judge0 CE Code Execution Client.
Handles compilation, sandboxed execution, and test evaluation of Java DSA code.
Provides time-limit and memory-limit configurations, and detailed compilation/runtime error retrieval.
"""

from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger

# Judge0 Language ID for Java (OpenJDK 17 / OpenJDK 13)
DEFAULT_JAVA_LANGUAGE_ID = 62


class Judge0ServiceClient:
    """
    Interface to Judge0 CE REST API for compiling and running Java DSA code.
    Enforces process isolation: untrusted student code is never executed inside FastAPI.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_host: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ):
        self.api_url = (api_url or settings.JUDGE0_API_URL).rstrip("/")
        self.api_key = api_key if api_key is not None else settings.JUDGE0_API_KEY
        self.api_host = api_host if api_host is not None else settings.JUDGE0_API_HOST
        self.timeout = timeout_seconds or settings.JUDGE0_TIMEOUT_SECONDS
        self.default_time_limit_sec = 4.0
        self.default_memory_limit_kb = 128000  # 128 MB

    def _get_headers(self) -> Dict[str, str]:
        """Constructs request headers, including RapidAPI authentication if configured."""
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
            async with httpx.AsyncClient(timeout=3.0) as client:
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
        language_id: int = DEFAULT_JAVA_LANGUAGE_ID,
        cpu_time_limit: Optional[float] = None,
        memory_limit_kb: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Submits Java code to Judge0 CE for synchronous execution.
        Distinguishes Compilation Errors, Runtime Errors, Time Limit Exceeded,
        Memory Limit Exceeded, and Output Mismatches.
        """
        health = await self.check_health()
        if not health["is_healthy"]:
            return {
                "status": "Execution Server Offline",
                "status_id": None,
                "is_passed": False,
                "stdout": None,
                "stderr": None,
                "compile_output": (
                    f"Judge0 CE server is offline at {self.api_url}. "
                    "Please launch Judge0 CE via Docker or configure JUDGE0_API_URL in backend/.env."
                ),
                "execution_time_ms": 0.0,
                "memory_kb": 0.0,
                "is_service_available": False,
                "error_type": "SERVICE_UNAVAILABLE",
            }

        url = f"{self.api_url}/submissions?base64_encoded=false&wait=true"
        payload = {
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin_input,
            "expected_output": expected_output,
            "cpu_time_limit": cpu_time_limit or self.default_time_limit_sec,
            "memory_limit": memory_limit_kb or self.default_memory_limit_kb,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self._get_headers())
                if response.status_code in (200, 201):
                    result = response.json()
                    status_info = result.get("status", {})
                    status_id = status_info.get("id")
                    status_desc = status_info.get("description", "Unknown")

                    stdout = result.get("stdout") or ""
                    stderr = result.get("stderr") or ""
                    compile_output = result.get("compile_output") or ""
                    time_taken_ms = float(result.get("time") or 0.0) * 1000.0
                    memory_kb = float(result.get("memory") or 0.0)

                    # Determine error categorization:
                    # Judge0 Status IDs:
                    # 3: Accepted
                    # 4: Wrong Answer
                    # 5: Time Limit Exceeded
                    # 6: Compilation Error
                    # 7-12: Runtime Error (SIGSEGV, SIGXFSZ, SIGFPE, SIGABRT, NZEC, etc.)
                    # 13: Internal Error
                    # 14: Exec Format Error
                    error_type = None
                    if status_id == 6:
                        error_type = "COMPILATION_ERROR"
                    elif status_id == 5:
                        error_type = "TIME_LIMIT_EXCEEDED"
                    elif status_id in (7, 8, 9, 10, 11, 12):
                        error_type = "RUNTIME_ERROR"
                    elif status_id == 4:
                        error_type = "WRONG_ANSWER"

                    # Passed check
                    is_passed = status_id == 3
                    if not is_passed and expected_output is not None and status_id == 4:
                        # Secondary normalization check
                        is_passed = stdout.strip() == expected_output.strip()

                    return {
                        "status": status_desc,
                        "status_id": status_id,
                        "is_passed": is_passed,
                        "stdout": stdout,
                        "stderr": stderr,
                        "compile_output": compile_output,
                        "execution_time_ms": round(time_taken_ms, 2),
                        "memory_kb": memory_kb,
                        "is_service_available": True,
                        "error_type": error_type,
                    }
                else:
                    return {
                        "status": "Submission Rejected",
                        "status_id": None,
                        "is_passed": False,
                        "stdout": None,
                        "stderr": response.text,
                        "compile_output": f"HTTP {response.status_code} from Judge0 server.",
                        "execution_time_ms": 0.0,
                        "memory_kb": 0.0,
                        "is_service_available": False,
                        "error_type": "SUBMISSION_REJECTED",
                    }
        except httpx.TimeoutException:
            return {
                "status": "Time Limit Exceeded",
                "status_id": 5,
                "is_passed": False,
                "stdout": None,
                "stderr": f"Execution exceeded client request timeout of {self.timeout}s.",
                "compile_output": None,
                "execution_time_ms": float(self.timeout * 1000.0),
                "memory_kb": 0.0,
                "is_service_available": True,
                "error_type": "TIME_LIMIT_EXCEEDED",
            }
        except Exception as exc:
            logger.error(f"Error querying Judge0: {exc}")
            return {
                "status": "Execution Transport Error",
                "status_id": None,
                "is_passed": False,
                "stdout": None,
                "stderr": str(exc),
                "compile_output": f"Network transport failure: {str(exc)}",
                "execution_time_ms": 0.0,
                "memory_kb": 0.0,
                "is_service_available": False,
                "error_type": "TRANSPORT_ERROR",
            }


# Singleton service instance
judge0_service = Judge0ServiceClient()
