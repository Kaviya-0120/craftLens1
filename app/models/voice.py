"""
Pydantic schemas for the voice pipeline:
  - /voice/transcribe
  - /voice/extract-fields
  - /voice/next-question
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# /voice/transcribe
# ─────────────────────────────────────────────

class TranscribeResponse(BaseModel):
    transcript: str = Field(..., description="Raw text produced by Whisper")
    detected_language: str = Field(
        ..., description="ISO 639-1 language code detected by Whisper, e.g. 'hi', 'en'"
    )


# ─────────────────────────────────────────────
# /voice/extract-fields
# ─────────────────────────────────────────────

class ExtractFieldsRequest(BaseModel):
    transcript: str = Field(..., description="Transcript text from /voice/transcribe")
    detected_language: str = Field(
        ..., description="Language code returned by /voice/transcribe"
    )


class ConfidencePerField(BaseModel):
    material: float = Field(..., ge=0.0, le=1.0)
    craft_technique: float = Field(..., ge=0.0, le=1.0)
    size: float = Field(..., ge=0.0, le=1.0)
    region: float = Field(..., ge=0.0, le=1.0)


class ExtractFieldsResponse(BaseModel):
    material: Optional[str] = Field(None, description="Primary material, e.g. 'silk', 'cotton'")
    craft_technique: Optional[str] = Field(
        None, description="Craft technique, e.g. 'block print', 'zari embroidery'"
    )
    size: Optional[str] = Field(None, description="Dimensions or size descriptor")
    region: Optional[str] = Field(None, description="Geographic origin, e.g. 'Varanasi', 'Rajasthan'")
    color: Optional[str] = Field(None, description="Primary color(s)")
    price_hint: Optional[str] = Field(
        None, description="Price mentioned by artisan, if any, as a raw string"
    )
    confidence_per_field: ConfidencePerField = Field(
        ..., description="Self-reported LLM confidence 0–1 per extractable field"
    )


# ─────────────────────────────────────────────
# /voice/next-question
# ─────────────────────────────────────────────

class NextQuestionRequest(BaseModel):
    structured_fields: ExtractFieldsResponse
    detected_language: str = Field(..., description="Artisan's language code")


class NextQuestionResponse(BaseModel):
    needs_followup: bool
    field: Optional[str] = Field(
        None, description="The field being asked about; null when needs_followup=false"
    )
    question_text: Optional[str] = Field(
        None, description="Spoken-style question in the artisan's language"
    )
    language: Optional[str] = Field(None, description="Language code of question_text")
