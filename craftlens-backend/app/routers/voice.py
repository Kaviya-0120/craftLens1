"""
Voice Router — Phase 1 & 2

  POST /voice/transcribe       audio file → transcript + language
  POST /voice/extract-fields   transcript → structured fields + confidence
  POST /voice/next-question    fields → follow-up question (active-learning loop)

Active-learning loop note (for frontend integration):
  1. POST /voice/transcribe              → { transcript, language }
  2. POST /voice/extract-fields          → { fields, confidence }
  3. POST /voice/next-question           → { needs_followup, field, question_text }
  4. If needs_followup=true:
       - Play question_text as TTS
       - Artisan responds by voice
       - POST /voice/transcribe (new audio) → new_transcript
       - POST /voice/extract-fields with
           transcript=new_transcript,
           previous_transcript=<original transcript>   ← context preserved
       - GOTO 3
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.schemas import (
    ExtractFieldsRequest,
    ExtractFieldsResponse,
    ExtractedFields,
    FieldConfidence,
    NextQuestionRequest,
    NextQuestionResponse,
    TranscribeResponse,
)
from app.services import asr_service, llm_service
from app.utils.errors import craft_error_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Voice Pipeline"])

# ── Priority order for follow-up (pricing relevance high → low) ───────────────
_FIELD_PRIORITY = ["material", "craft_technique", "size", "region"]

_FIELD_LABELS = {
    "material": "the primary material (e.g. silk, cotton, brass)",
    "craft_technique": "the craft technique or weaving/printing method",
    "size": "the size or dimensions of the product",
    "region": "the geographic region or craft cluster of origin",
}


# ─────────────────────────────────────────────────────────────────────────────
# POST /voice/transcribe
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    summary="Transcribe audio to text",
    description="Upload an audio file (webm/mp3/wav/m4a). Returns transcript and detected language.",
)
async def transcribe_audio(
    file: Annotated[UploadFile, File(description="Audio file — webm, mp3, wav, or m4a")],
):
    if not file or not file.filename:
        return craft_error_response(400, "No audio file provided.")

    audio_bytes = await file.read()
    if not audio_bytes:
        return craft_error_response(400, "Uploaded file is empty.")

    try:
        result = asr_service.transcribe(audio_bytes, file.filename)
        return TranscribeResponse(
            transcript=result.transcript,
            detected_language=result.detected_language,
            confidence=result.confidence,
        )
    except ValueError as exc:
        return craft_error_response(422, str(exc), exc, log_traceback=False)
    except RuntimeError as exc:
        return craft_error_response(500, "ASR transcription failed.", exc)
    except Exception as exc:
        return craft_error_response(500, "Unexpected error during transcription.", exc)


# ─────────────────────────────────────────────────────────────────────────────
# POST /voice/extract-fields
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/extract-fields",
    response_model=ExtractFieldsResponse,
    summary="Extract structured craft fields from transcript",
    description=(
        "Pass transcript + language. Optionally pass previous_transcript to "
        "concatenate context from prior turns (active-learning loop)."
    ),
)
async def extract_fields(body: ExtractFieldsRequest):
    # Merge transcripts if previous context exists
    if body.previous_transcript:
        full_transcript = f"{body.previous_transcript.strip()} {body.transcript.strip()}"
    else:
        full_transcript = body.transcript.strip()

    system_prompt = llm_service.load_prompt("field_extraction")
    user_prompt = (
        f"Language: {body.language}\n\n"
        f"Transcript:\n{full_transcript}"
    )

    raw = None
    try:
        raw = llm_service.call_llm(system_prompt, user_prompt, json_mode=True)
        data = llm_service.parse_llm_json(raw)
    except ValueError:
        # Retry once with stronger JSON reminder
        logger.warning("JSON parse failed on first attempt — retrying with stricter prompt.")
        retry_prompt = user_prompt + "\n\nIMPORTANT: Return ONLY a valid JSON object. No text before or after."
        try:
            raw = llm_service.call_llm(system_prompt, retry_prompt, json_mode=True)
            data = llm_service.parse_llm_json(raw)
        except ValueError as exc:
            return craft_error_response(422, "LLM did not return valid JSON after retry.", exc)
    except RuntimeError as exc:
        return craft_error_response(500, "LLM call failed.", exc)
    except Exception as exc:
        return craft_error_response(500, "Unexpected error during field extraction.", exc)

    # Normalise confidence block
    conf_raw = data.get("confidence") or {}
    confidence = FieldConfidence(
        material=float(conf_raw.get("material", 0.0)),
        craft_technique=float(conf_raw.get("craft_technique", 0.0)),
        size=float(conf_raw.get("size", 0.0)),
        region=float(conf_raw.get("region", 0.0)),
    )

    fields = ExtractedFields(
        material=data.get("material"),
        craft_technique=data.get("craft_technique"),
        size=data.get("size"),
        region=data.get("region"),
        color=data.get("color"),
        price_hint=_safe_float(data.get("price_hint")),
    )

    return ExtractFieldsResponse(
        fields=fields,
        confidence=confidence,
        transcript_used=full_transcript,
    )


def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# POST /voice/next-question
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/next-question",
    response_model=NextQuestionResponse,
    summary="Get the next follow-up question for the artisan",
    description=(
        "Finds the highest-priority field below the confidence threshold and "
        "returns a single natural spoken question in the artisan's language. "
        "Returns needs_followup=false when all key fields are confident."
    ),
)
async def next_question(body: NextQuestionRequest):
    threshold = settings.confidence_threshold
    conf = body.confidence.model_dump()

    # Walk fields in priority order
    weakest_field = None
    for field in _FIELD_PRIORITY:
        if conf.get(field, 0.0) < threshold:
            weakest_field = field
            break

    if weakest_field is None:
        return NextQuestionResponse(needs_followup=False)

    field_label = _FIELD_LABELS.get(weakest_field, weakest_field)
    current_value = getattr(body.fields, weakest_field, None)

    system_prompt = llm_service.load_prompt("followup_question")
    user_prompt = (
        f"Language: {body.language}\n"
        f"Ask about: {field_label}\n"
        f"Current extracted value (may be null or vague): {current_value}"
    )

    try:
        question_text = llm_service.call_llm(
            system_prompt, user_prompt, json_mode=False
        ).strip()
    except RuntimeError as exc:
        return craft_error_response(500, "LLM call failed.", exc)
    except Exception as exc:
        return craft_error_response(500, "Unexpected error generating follow-up question.", exc)

    return NextQuestionResponse(
        needs_followup=True,
        field=weakest_field,
        question_text=question_text,
        language=body.language,
    )
