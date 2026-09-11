"""
All Pydantic request/response schemas for CraftLens API.

Organised by phase. Import from here in all routers/services.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# COMMON
# ═══════════════════════════════════════════════════════════

class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"


# ═══════════════════════════════════════════════════════════
# PHASE 1 — VOICE / ASR
# ═══════════════════════════════════════════════════════════

class TranscribeResponse(BaseModel):
    transcript: str = Field(..., description="Raw text produced by the ASR engine")
    detected_language: str = Field(..., description="ISO 639-1 language code, e.g. 'hi', 'en', 'ta'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="ASR confidence score (Whisper always returns 1.0)")


class FieldConfidence(BaseModel):
    material: float = Field(..., ge=0.0, le=1.0)
    craft_technique: float = Field(..., ge=0.0, le=1.0)
    size: float = Field(..., ge=0.0, le=1.0)
    region: float = Field(..., ge=0.0, le=1.0)


class ExtractedFields(BaseModel):
    material: Optional[str] = None
    craft_technique: Optional[str] = None
    size: Optional[str] = None
    region: Optional[str] = None
    color: Optional[str] = None
    price_hint: Optional[float] = None


class ExtractFieldsRequest(BaseModel):
    transcript: str = Field(..., description="Transcript from /voice/transcribe")
    language: str = Field(..., description="ISO language code from /voice/transcribe")
    previous_transcript: Optional[str] = Field(
        None,
        description=(
            "Transcript from a previous turn — if provided, concatenated with "
            "`transcript` before extraction so context is not lost across turns."
        ),
    )


class ExtractFieldsResponse(BaseModel):
    fields: ExtractedFields
    confidence: FieldConfidence
    transcript_used: str = Field(..., description="The full transcript that was passed to the LLM")


# ═══════════════════════════════════════════════════════════
# PHASE 2 — FOLLOW-UP QUESTION
# ═══════════════════════════════════════════════════════════

class NextQuestionRequest(BaseModel):
    fields: ExtractedFields
    confidence: FieldConfidence
    language: str = Field(..., description="Artisan's language code for question phrasing")


class NextQuestionResponse(BaseModel):
    needs_followup: bool
    field: Optional[str] = Field(None, description="Field being asked about")
    question_text: Optional[str] = Field(None, description="Spoken-style question in artisan's language")
    language: Optional[str] = None


# ═══════════════════════════════════════════════════════════
# PHASE 3 — IMAGE PIPELINE
# ═══════════════════════════════════════════════════════════

class ProcessImageResponse(BaseModel):
    processed_image_url: str = Field(..., description="Relative URL: /static/{uuid}.png")
    image_id: str = Field(..., description="UUID string of the saved image")


class VisualTag(BaseModel):
    label: str
    score: float = Field(..., ge=0.0, le=1.0)


class ImageTagRequest(BaseModel):
    image_id: str = Field(..., description="UUID from /image/process")


class ImageTagResponse(BaseModel):
    visual_tags: List[VisualTag] = Field(..., description="Top-3 CLIP tags with confidence scores")


# ═══════════════════════════════════════════════════════════
# PHASE 4 — LISTING GENERATION
# ═══════════════════════════════════════════════════════════

class GenerateListingRequest(BaseModel):
    fields: ExtractedFields
    transcript_original_language: str = Field(
        ..., description="Original artisan transcript in their language"
    )
    language: str = Field(..., description="ISO language code of the artisan")


class GenerateListingResponse(BaseModel):
    title_regional: str
    title_english: str
    description_regional: str
    description_english: str


# ═══════════════════════════════════════════════════════════
# PHASE 5 — PRICING ENGINE
# ═══════════════════════════════════════════════════════════

class PricingEstimateRequest(BaseModel):
    fields: ExtractedFields
    listing_text: str = Field(..., description="Generated listing title+description for embedding")


class ComparableSample(BaseModel):
    title: str
    price: float
    category: str


class PricingEstimateResponse(BaseModel):
    price_range: List[float] = Field(..., min_length=2, max_length=2)
    median_price: float
    comparable_count: int
    comparable_samples: List[ComparableSample]
    low_confidence: bool = Field(
        False,
        description="True if fewer than 3 comparables found after filtered search",
    )


# ═══════════════════════════════════════════════════════════
# PHASE 6 — CROSS-MODAL CONSISTENCY
# ═══════════════════════════════════════════════════════════

class ConsistencyCheckRequest(BaseModel):
    voice_material: str = Field(..., description="Material extracted from voice")
    voice_craft: str = Field(..., description="Craft technique extracted from voice")
    visual_tags: List[VisualTag]
    language: str = Field(default="en", description="Language for confirmation question")


class ConsistencyCheckResponse(BaseModel):
    mismatch: bool
    voice_claim: str
    closest_visual_tag: str
    similarity_score: float
    confirmation_question: Optional[str] = Field(
        None, description="LLM-generated clarification question; null if no mismatch"
    )


# ═══════════════════════════════════════════════════════════
# PHASE 7 — EXPLAINABLE / CONTESTABLE PRICING
# ═══════════════════════════════════════════════════════════

class PricingExplainRequest(BaseModel):
    pricing_result: PricingEstimateResponse
    fields: ExtractedFields
    language: str = Field(default="en")


class PricingExplainResponse(BaseModel):
    explanation_text: str
    language: str


class PricingContestRequest(BaseModel):
    correction_transcript: str = Field(..., description="Artisan's spoken pushback / correction")
    language: str
    original_fields: ExtractedFields


class PricingContestResponse(BaseModel):
    updated_fields: ExtractedFields
    updated_pricing: PricingEstimateResponse
    updated_explanation: str


# ═══════════════════════════════════════════════════════════
# PHASE 8 — CATALOGUE PUBLISH
# ═══════════════════════════════════════════════════════════

class PublishRequest(BaseModel):
    image_url: str
    title_regional: str
    title_english: str
    description_regional: str
    description_english: str
    price: float
    fields: ExtractedFields


class PublishResponse(BaseModel):
    listing_id: str = Field(..., description="UUID of the new listing record")
    share_url: str = Field(..., description="Shareable stub URL: /listing/{uuid}")


class ListingRecord(BaseModel):
    id: str
    image_url: str
    title_regional: str
    title_english: str
    description_regional: str
    description_english: str
    price: float
    fields: Dict[str, Any]
    created_at: str
