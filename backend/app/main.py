"""
Main Application Entry Point.
Initializes FastAPI, registers CORS, global exception handlers, and API v1 routing.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import logger
from app.routes.api import api_v1_router
from app.utilities.exceptions import AppException
from app.utilities.response import error_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager handling database bootstrap and background tasks."""
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode.")
    # Initialize DB tables and seed curriculum
    init_db()
    logger.info("Application startup sequence completed.")
    yield
    logger.info("Application shutdown completed.")


# Initialize FastAPI instance
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Intelligent One-to-One Learning Support System for IT22301: Data Structures and Algorithms. "
        "Provides Bayesian Knowledge Tracing (BKT), multi-tier progressive scaffolding, "
        "cognitive misconception diagnosis, and Judge0 Java execution."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Domain Exception Handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handles domain-specific application exceptions cleanly."""
    logger.warning(f"Domain exception: {exc.message} (status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=exc.message, error=exc.details).dict(),
    )


# Fallback Generic Exception Handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catches uncaught exceptions to ensure consistent JSON envelope."""
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="An unexpected internal server error occurred.",
            error=str(exc) if settings.DEBUG else None,
        ).dict(),
    )


# Root Discovery Endpoint
@app.get("/", tags=["Discovery"])
def read_root():
    """Root endpoint for API service discovery and status check."""
    return {
        "service": settings.APP_NAME,
        "course": "IT22301 – Data Structures and Algorithms",
        "status": "online",
        "api_v1_docs": "/docs",
        "health_check": "/api/v1/health",
    }


# Mount API v1 Routers
app.include_router(api_v1_router, prefix="/api/v1")
# Root-level health check endpoint convenience
app.include_router(api_v1_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
