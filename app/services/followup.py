"""
Follow-up question service — Phase 2.

Identifies the lowest-confidence required field and generates a single,
natural spoken-style question in the artisan's language.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.llm_client import chat_completion

logger = logging.getLogger(__name__)

# Fields in descending priority for pricing relevance
_FIELD_PRIORITY = ["material", "craft_technique", "size", "region"]
_CONFIDENCE_THRESHOLD = 0.7

_FIELD_LABELS = {
    "material": "the primary material used",
    "craft_technique": "the craft technique or weaving/printing method",
    "size": "the size or dimensions",
    "region": "the region or place of origin",
}

_SYSTEM_PROMPT = """\
You are a helpful assistant talking to an Indian artisan in their native language.
Your task is to ask ONE short, natural, conversational follow-up question to gather
missing product information. 

Rules:
- Ask only about the specific field mentioned in the user message.
- Use simple, spoken language — as if you are having a friendly chat.
- Write the question in the language code specified.
- Return ONLY the question text — no JSON, no labels, no extra words.
"""


async def generate_next_question(
    structured_fields: dict[str, Any],
    detected_language: str,
) -> dict[str, Any]:
    """
    Find the weakest required field and ask about it.

    Returns a dict matching NextQuestionResponse.
    """
    confidence = structured_fields.get("confidence_per_field", {})

    # Walk fields in priority order; pick first one below threshold
    weakest_field: str | None = None
    for field in _FIELD_PRIORITY:
        score = float(confidence.get(field, 0.0))
        if score < _CONFIDENCE_THRESHOLD:
            weakest_field = field
            break

    if weakest_field is None:
        logger.info("All fields above threshold — no follow-up needed.")
        return {"needs_followup": False, "field": None, "question_text": None, "language": None}

    logger.info(
        "Weakest field: '%s' (confidence=%.2f) — generating follow-up question.",
        weakest_field,
        float(confidence.get(weakest_field, 0.0)),
    )

    field_description = _FIELD_LABELS.get(weakest_field, weakest_field)
    user_msg = (
        f"Language: {detected_language}\n"
        f"Ask the artisan about: {field_description}\n"
        f"Current value (may be null or vague): {structured_fields.get(weakest_field)}"
    )

    question_text = chat_completion(
        system_prompt=_SYSTEM_PROMPT,
        user_message=user_msg,
        temperature=0.4,
        max_tokens=128,
    ).strip()

    return {
        "needs_followup": True,
        "field": weakest_field,
        "question_text": question_text,
        "language": detected_language,
    }
