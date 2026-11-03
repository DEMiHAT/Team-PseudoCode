"""
Health and diagnostics routes.
Reports overall system status, SQLite/PostgreSQL connectivity, and external integration health.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db
from app.services.gemini_service import gemini_service
from app.services.judge0_service import judge0_service
from app.schemas.health import HealthResponse, ServiceStatus
from app.utilities.response import ApiResponse, success_response

router = APIRouter()


@router.get("/health", response_model=ApiResponse[HealthResponse], summary="System Health & Diagnostic Check")
async def get_system_health(db: Session = Depends(get_db)):
    """
    Verifies backend server, database responsiveness, and external service endpoints.
    """
    # 1. Database Connectivity Probe
    db_ok = False
    try:
        db.execute(text("SELECT 1")).scalar()
        db_ok = True
    except Exception:
        db_ok = False

    # 2. Check external services
    gemini_health = await gemini_service.check_health()
    judge0_health = await judge0_service.check_health()

    health_payload = HealthResponse(
        status="operational" if db_ok else "degraded",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        database_connected=db_ok,
        services={
            "gemini": ServiceStatus(**gemini_health),
            "judge0": ServiceStatus(**judge0_health),
        },
        timestamp=datetime.now(timezone.utc),
    )

    return success_response(
        data=health_payload,
        message="System health status retrieved successfully",
    )

