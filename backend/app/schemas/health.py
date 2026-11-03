"""
Pydantic schemas for application health and external integration monitoring.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class ServiceStatus(BaseModel):
    name: str
    status: str  # online, offline, unconfigured, degraded
    is_healthy: bool
    endpoint: Optional[str] = None
    message: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    database_connected: bool
    services: Dict[str, ServiceStatus]
    timestamp: datetime
