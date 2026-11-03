"""
Application custom exceptions for domain-level error handling.
"""

from typing import Any, Optional


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class ResourceNotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource_name: str, identifier: Any):
        super().__init__(
            message=f"{resource_name} with identifier '{identifier}' was not found.",
            status_code=404,
        )


class ExternalServiceException(AppException):
    """Raised when an upstream third-party service (e.g. Judge0, Gemini) encounters an error."""

    def __init__(self, service_name: str, details: Any = None):
        super().__init__(
            message=f"External service '{service_name}' failed to respond or returned an error.",
            status_code=502,
            details=details,
        )


class CodeExecutionException(AppException):
    """Raised when code compilation or execution cannot be processed."""

    def __init__(self, message: str, details: Any = None):
        super().__init__(
            message=message,
            status_code=422,
            details=details,
        )

