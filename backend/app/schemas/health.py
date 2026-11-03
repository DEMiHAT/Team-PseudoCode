"""
Pydantic schemas for API health and diagnostics.
"""

from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for health-check endpoint response."""
    status: str = Field(default="ok", example="ok")
    app_name: str = Field(..., example="Empowering the Individual - Learning Support API")
    environment: str = Field(..., example="development")
    database_connected: bool = Field(default=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)

