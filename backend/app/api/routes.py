"""
API routes for health check and system verification.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the status of the API service and verifies database connectivity.",
)
def health_check(db: Session = Depends(get_db)):
    """
    Verifies that the FastAPI server is running and can interact with the SQLite database.
    """
    db_connected = False
    details = {}

    try:
        # Run a lightweight query to test SQLite connection
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            db_connected = True
            details["database"] = "SQLite connected successfully"
    except Exception as exc:
        details["database_error"] = str(exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "degraded",
                "message": "Database connectivity failed",
                "error": str(exc),
            },
        )

    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        database_connected=db_connected,
        timestamp=datetime.now(timezone.utc),
        details=details,
    )

