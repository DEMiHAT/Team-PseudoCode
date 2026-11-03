"""
Main entry point for the FastAPI application.
Configures CORS, registers database initialization on startup, and sets up routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs database schema creation on startup.
    """
    # Startup: ensure SQLite tables exist
    print("[*] Initializing database tables...")
    init_db()
    print("[+] Database tables initialized successfully.")
    yield
    # Shutdown logic (if any) can be placed here
    print("[-] Shutting down application...")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Adaptive AI Learning Platform for Class 8 Mathematics. Provides Bayesian Knowledge Tracing and misconception diagnostics.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure Cross-Origin Resource Sharing (CORS)
# Allows the React Vite frontend to communicate with this backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global generic error handler for unexpected server exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback handler for uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected server error occurred.",
            "detail": str(exc) if settings.DEBUG else "Internal server error",
        },
    )


# Root route for quick verification in the browser
@app.get("/", tags=["General"])
def read_root():
    """Welcome endpoint for API discovery."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "status": "running",
        "docs_url": "/docs",
        "health_check": "/api/health",
    }


# Include API routes under /api and root for convenience
app.include_router(api_router, prefix="/api", tags=["System"])
app.include_router(api_router, tags=["System"])  # allows /health as well as /api/health


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

