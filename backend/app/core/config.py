"""
Configuration settings module using Pydantic Settings.
Loads configuration from environment variables or .env file.
"""

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings."""

    APP_NAME: str = "Empowering the Individual - Learning Support API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # SQLite Database connection string
    # "check_same_thread=False" is handled in database.py for SQLite
    DATABASE_URL: str = "sqlite:///./learning_platform.db"

    # Allowed CORS origins for the frontend React app
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://127.0.0.1:5173"

    # Optional LLM integration (fallback to static responses if empty)
    LLM_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


# Global singleton instance for settings
settings = Settings()

