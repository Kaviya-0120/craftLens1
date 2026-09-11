"""
Field extraction service — Phase 1, step 2.

Sends the artisan's transcript to the LLM and asks it to return a strict
JSON object with craft metadata + self-reported per-field confidence.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.llm_client import chat_completion
from app.utils.json_parser import extract_json

logger = logging.getLogger(__name__)


# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are an expert craft-product cataloguing assistant for Indian artisans.
Your job is to extract structured product information from a spoken transcript.

Return ONLY a single valid JSON object — no prose, no markdown fences, no extra keys.

The JSON must have exactly these keys:
{
  "material": <string or null>,
  "craft_technique": <string or null>,
  "size": <string or null>,
  "region": <string or null>,
  "color": <string or null>,
  "price_hint": <string or null>,
  "confidence_per_field": {
    "material": <float 0.0–1.0>,
    "craft_technique": <float 0.0–1.0>,
    "size": <float 0.0–1.0>,
    "region": <float 0.0–1.0>
  }
}

Confidence scoring rules — be honest, not generous:
- 1.0 : artisan stated this field explicitly and unambiguously
- 0.7–0.9 : field is strongly implied or described in clear context
- 0.4–0.6 : field is vaguely mentioned or can only be inferred with uncertainty
- 0.1–0.3 : field is barely hinted at
- 0.0 : field was not mentioned at all (set value to null)

Extract values in the ORIGINAL language of the transcript where appropriate.
For region, prefer the most specific place name mentioned.
For price_hint, capture the artisan's own words verbatim (e.g. "teen sau rupaye").
"""


def _build_user_message(transcript: str, language: str) -> str:
    return (
        f"Transcript language: {language}\n\n"
        f"Transcript:\n{transcript}"
    )


# ── Core service function ─────────────────────────────────────────────────────

async def extract_fields(transcript: str, detected_language: str) -> dict[str, Any]:
    """
    Extract craft metadata from a transcript using the configured LLM.

    Returns a dict matching the ExtractFieldsResponse schema.

    Raises
    ------
    RuntimeError  on LLM or JSON-parsing failure.
    ValueError    if the LLM response cannot be parsed as JSON.
    """
    user_msg = _build_user_message(transcript, detected_language)

    raw_response = chat_completion(
        system_prompt=_SYSTEM_PROMPT,
        user_message=user_msg,
        temperature=0.1,   # low temperature for deterministic structured output
        max_tokens=512,
    )

    try:
        data = extract_json(raw_response)
    except ValueError as exc:
        raise ValueError(f"Field extraction: {exc}") from exc

    # Normalise — ensure all expected keys exist with safe defaults
    confidence = data.get("confidence_per_field") or {}
    return {
        "material": data.get("material"),
        "craft_technique": data.get("craft_technique"),
        "size": data.get("size"),
        "region": data.get("region"),
        "color": data.get("color"),
        "price_hint": data.get("price_hint"),
        "confidence_per_field": {
            "material": float(confidence.get("material", 0.0)),
            "craft_technique": float(confidence.get("craft_technique", 0.0)),
            "size": float(confidence.get("size", 0.0)),
            "region": float(confidence.get("region", 0.0)),
        },
    }
