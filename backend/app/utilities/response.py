"""
Standardized API response format and helper functions.
Provides a predictable JSON envelope for all API endpoints.
"""

from typing import Generic, TypeVar, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    """Standard unified response wrapper for all API endpoints."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(default="Operation completed successfully", description="User or system message")
    data: Optional[DataT] = Field(default=None, description="Payload data")
    error: Optional[Any] = Field(default=None, description="Error details if success is False")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def success_response(data: Any = None, message: str = "Operation completed successfully") -> ApiResponse:
    """Convenience helper to construct a successful ApiResponse."""
    return ApiResponse(
        success=True,
        message=message,
        data=data,
        error=None,
    )


def error_response(message: str, error: Any = None) -> ApiResponse:
    """Convenience helper to construct a failed ApiResponse."""
    return ApiResponse(
        success=False,
        message=message,
        data=None,
        error=error,
    )
