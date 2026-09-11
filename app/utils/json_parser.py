"""
Utility to reliably extract a JSON object from an LLM response string.

LLMs sometimes wrap JSON in markdown fences (```json … ```) or add
surrounding prose. This parser strips those and returns a parsed dict.
"""

from __future__ import annotations

import json
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


def extract_json(text: str) -> dict[str, Any]:
    """
    Extract the first JSON object from `text`.

    Strategy:
    1. Strip markdown code fences if present.
    2. Try direct json.loads on the cleaned string.
    3. Fall back to a regex search for the first {...} block.

    Raises
    ------
    ValueError  if no valid JSON object can be found.
    """
    # 1. Strip markdown fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()

    # 2. Direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Regex fallback — grab the first {...} block (handles leading prose)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.error("Could not extract JSON from LLM output:\n%s", text)
    raise ValueError(
        "LLM did not return valid JSON. Raw response logged at ERROR level."
    )
