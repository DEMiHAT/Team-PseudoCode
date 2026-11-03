"""
Common shared Pydantic schemas and enums.
"""

from typing import Generic, TypeVar, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiResponseSchema(BaseModel, Generic[DataT]):
    """Standardized response schema."""

    success: bool
    message: str = "Operation completed successfully"
    data: Optional[DataT] = None
    error: Optional[Any] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
