"""
Application configuration management using Pydantic Settings.
Loads and validates settings from environment variables and .env files.
"""

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings with strict validation."""

    # Application Information
    APP_NAME: str = "IT22301 DSA Intelligent Tutoring System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database Configuration (Supports SQLite and PostgreSQL)
    DATABASE_URL: str = "sqlite:///./dsa_tutor.db"

    # CORS Security Configuration
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://127.0.0.1:5173"

    # Logging
    LOG_LEVEL: str = "INFO"

    # External Integration: Google Gemini (LLM Tutoring)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # External Integration: Judge0 CE (Java Code Execution)
    JUDGE0_API_URL: str = "http://localhost:2358"
    JUDGE0_API_KEY: str = ""
    JUDGE0_API_HOST: str = ""
    JUDGE0_TIMEOUT_SECONDS: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        """Ensures CORS_ORIGINS is always a list of clean URL strings."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_sqlite(self) -> bool:
        """Returns True if database engine is SQLite."""
        return self.DATABASE_URL.startswith("sqlite")


# Global application settings instance
settings = Settings()
