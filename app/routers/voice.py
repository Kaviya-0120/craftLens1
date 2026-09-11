"""
Voice pipeline router — Phase 1 & 2 endpoints.

  POST /voice/transcribe       — audio file → transcript + language
  POST /voice/extract-fields   — transcript → structured craft fields
  POST /voice/next-question    — fields → follow-up question (Phase 2, stub here)
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.voice import (
    TranscribeResponse,
    ExtractFieldsRequest,
    ExtractFieldsResponse,
    ConfidencePerField,
    NextQuestionRequest,
    NextQuestionResponse,
)
from app.models.common import ErrorResponse
from app.services.transcription import transcribe_audio
from app.services.field_extraction import extract_fields

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice Pipeline"])

# ── Allowed audio MIME types ──────────────────────────────────────────────────
_ALLOWED_CONTENT_TYPES = {
    "audio/webm",
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/ogg",
    "audio/mp4",
    "video/webm",        # Chrome sometimes sends webm with video/* type
    "application/octet-stream",  # fallback for generic uploads
}


# ─────────────────────────────────────────────────────────────────────────────
# POST /voice/transcribe
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Unsupported file type"},
        500: {"model": ErrorResponse, "description": "Transcription failed"},
    },
    summary="Transcribe an audio file with Whisper",
    description=(
        "Upload a webm / mp3 / wav audio file. "
        "Whisper (self-hosted) transcribes it and auto-detects the language. "
        "Returns the raw transcript and an ISO 639-1 language code."
    ),
)
async def transcribe_endpoint(
    file: Annotated[UploadFile, File(description="Audio file (webm, mp3, wav, ogg)")],
) -> TranscribeResponse:
    # Light content-type guard (browsers sometimes lie, so not a hard block)
    if file.content_type and file.content_type not in _ALLOWED_CONTENT_TYPES:
        logger.warning(
            "Unusual content-type '%s' — proceeding anyway.", file.content_type
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required to infer audio format.",
        )

    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        result = await transcribe_audio(audio_bytes, file.filename)
        return TranscribeResponse(**result)

    except HTTPException:
        raise
    except RuntimeError as exc:
        logger.error("Transcription error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error in /voice/transcribe")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {exc}",
        )


# ─────────────────────────────────────────────────────────────────────────────
# POST /voice/extract-fields
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/extract-fields",
    response_model=ExtractFieldsResponse,
    responses={
        422: {"model": ErrorResponse, "description": "LLM returned unparseable JSON"},
        500: {"model": ErrorResponse, "description": "LLM call failed"},
    },
    summary="Extract structured craft fields from a transcript",
    description=(
        "Pass the transcript and detected language from /voice/transcribe. "
        "An LLM extracts material, craft_technique, size, region, color, "
        "price_hint, and self-reported confidence per field."
    ),
)
async def extract_fields_endpoint(body: ExtractFieldsRequest) -> ExtractFieldsResponse:
    try:
        result = await extract_fields(body.transcript, body.detected_language)
        return ExtractFieldsResponse(
            material=result["material"],
            craft_technique=result["craft_technique"],
            size=result["size"],
            region=result["region"],
            color=result["color"],
            price_hint=result["price_hint"],
            confidence_per_field=ConfidencePerField(**result["confidence_per_field"]),
        )

    except ValueError as exc:
        logger.warning("JSON parse error in /voice/extract-fields: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except RuntimeError as exc:
        logger.error("LLM error in /voice/extract-fields: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error in /voice/extract-fields")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {exc}",
        )


# ─────────────────────────────────────────────────────────────────────────────
# POST /voice/next-question  (Phase 2 — implemented in full below)
# ─────────────────────────────────────────────────────────────────────────────

# Priority order for follow-up: these fields matter most for pricing
_FIELD_PRIORITY = ["material", "craft_technique", "size", "region"]
_CONFIDENCE_THRESHOLD = 0.7


@router.post(
    "/next-question",
    response_model=NextQuestionResponse,
    responses={
        500: {"model": ErrorResponse, "description": "LLM call failed"},
    },
    summary="Get the next follow-up question for the artisan (active-learning loop)",
    description=(
        "Pass the extracted fields + confidence scores. "
        "Returns the single most important follow-up question in the artisan's "
        "language, or needs_followup=false if all key fields are confident enough. "
        "Re-call after each voice answer to drive the active-learning loop."
    ),
)
async def next_question_endpoint(body: NextQuestionRequest) -> NextQuestionResponse:
    from app.services.followup import generate_next_question  # local import avoids circular

    try:
        result = await generate_next_question(
            structured_fields=body.structured_fields.model_dump(),
            detected_language=body.detected_language,
        )
        return NextQuestionResponse(**result)

    except RuntimeError as exc:
        logger.error("LLM error in /voice/next-question: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error in /voice/next-question")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {exc}",
        )
