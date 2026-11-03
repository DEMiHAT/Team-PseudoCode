"""
Pydantic schemas for Preference entity.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PreferenceBase(BaseModel):
    preferred_language: str = Field(default="java")
    theme: str = Field(default="dark")
    editor_font_size: int = Field(default=14, ge=10, le=24)
    scaffolding_verbosity: str = Field(default="balanced")  # minimal, balanced, detailed
    audio_explanations_enabled: bool = False


class PreferenceCreate(PreferenceBase):
    student_id: int


class PreferenceUpdate(BaseModel):
    preferred_language: Optional[str] = None
    theme: Optional[str] = None
    editor_font_size: Optional[int] = None
    scaffolding_verbosity: Optional[str] = None
    audio_explanations_enabled: Optional[bool] = None


class PreferenceResponse(PreferenceBase):
    id: int
    student_id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
