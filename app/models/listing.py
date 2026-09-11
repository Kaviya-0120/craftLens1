"""
Pydantic schemas for the listing generation pipeline:
  - /listing/generate
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

from app.models.voice import ExtractFieldsResponse


# ─────────────────────────────────────────────
# /listing/generate
# ─────────────────────────────────────────────

class GenerateListingRequest(BaseModel):
    structured_fields: ExtractFieldsResponse = Field(
        ..., description="Extracted craft fields from /voice/extract-fields"
    )
    transcript: str = Field(
        ..., description="Original transcript — gives the LLM the artisan's own words"
    )


class GenerateListingResponse(BaseModel):
    title_regional: str = Field(
        ..., description="Product title in the artisan's regional language"
    )
    title_english: str = Field(..., description="Product title in English")
    description_regional: str = Field(
        ..., description="Full product description in the regional language"
    )
    description_english: str = Field(
        ..., description="Full SEO-friendly product description in English"
    )
