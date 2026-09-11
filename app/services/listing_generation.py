"""
Listing generation service — Phase 1, step 3.

Takes the structured craft fields + the original transcript and asks the LLM
to produce bilingual, SEO-friendly e-commerce listing copy.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.llm_client import chat_completion
from app.utils.json_parser import extract_json

logger = logging.getLogger(__name__)


# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a bilingual e-commerce copywriter specialising in Indian handcraft products.
Given structured product fields and the artisan's original spoken transcript,
write compelling, SEO-friendly product listing copy.

Return ONLY a single valid JSON object — no prose, no markdown fences.

The JSON must have exactly these keys:
{
  "title_regional": <string — product title in the regional language of the transcript>,
  "title_english": <string — product title in English, max 80 characters>,
  "description_regional": <string — 3–5 sentence product description in the regional language>,
  "description_english": <string — 3–5 sentence SEO product description in English>
}

Guidelines:
- English titles: include material, technique, and region if known (good for SEO).
- Descriptions: mention craft heritage, usability, and care tips if inferable.
- Regional text: write in the same script as the transcript language (Devanagari for Hindi, etc.).
- Do NOT invent facts not present in the fields or transcript.
- Tone: warm, artisan-authentic, e-commerce ready.
"""


def _build_user_message(structured_fields: dict, transcript: str) -> str:
    fields_str = "\n".join(
        f"  {k}: {v}" for k, v in structured_fields.items() if k != "confidence_per_field"
    )
    return (
        f"Structured fields:\n{fields_str}\n\n"
        f"Original transcript:\n{transcript}"
    )


# ── Core service function ─────────────────────────────────────────────────────

async def generate_listing(
    structured_fields: dict[str, Any], transcript: str
) -> dict[str, str]:
    """
    Generate bilingual listing copy from structured fields + transcript.

    Returns a dict matching GenerateListingResponse.

    Raises
    ------
    RuntimeError  on LLM failure.
    ValueError    if JSON cannot be parsed from the LLM response.
    """
    user_msg = _build_user_message(structured_fields, transcript)

    raw_response = chat_completion(
        system_prompt=_SYSTEM_PROMPT,
        user_message=user_msg,
        temperature=0.5,   # slightly creative for copy generation
        max_tokens=1024,
    )

    try:
        data = extract_json(raw_response)
    except ValueError as exc:
        raise ValueError(f"Listing generation: {exc}") from exc

    return {
        "title_regional": data.get("title_regional", ""),
        "title_english": data.get("title_english", ""),
        "description_regional": data.get("description_regional", ""),
        "description_english": data.get("description_english", ""),
    }
