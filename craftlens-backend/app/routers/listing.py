"""
Listing Router — Phase 4

  POST /listing/generate   structured fields + transcript → bilingual SEO copy
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from app.models.schemas import GenerateListingRequest, GenerateListingResponse
from app.services import llm_service
from app.utils.errors import craft_error_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/listing", tags=["Listing Generation"])


@router.post(
    "/generate",
    response_model=GenerateListingResponse,
    summary="Generate bilingual e-commerce listing copy",
    description=(
        "Pass structured fields + original transcript. "
        "Returns SEO-optimised title and description in both English "
        "and the artisan's regional language."
    ),
)
async def generate_listing(body: GenerateListingRequest):
    system_prompt = llm_service.load_prompt("listing_generation")

    fields_str = "\n".join(
        f"  {k}: {v}"
        for k, v in body.fields.model_dump().items()
        if v is not None
    )

    user_prompt = (
        f"Artisan language: {body.language}\n\n"
        f"Product fields:\n{fields_str}\n\n"
        f"Original transcript (artisan's words):\n{body.transcript_original_language}"
    )

    raw = None
    try:
        raw = llm_service.call_llm(system_prompt, user_prompt, json_mode=True)
        data = llm_service.parse_llm_json(raw)
    except ValueError as exc:
        return craft_error_response(422, "LLM did not return valid JSON.", exc)
    except RuntimeError as exc:
        return craft_error_response(500, "LLM call failed.", exc)
    except Exception as exc:
        return craft_error_response(500, "Unexpected error generating listing.", exc)

    return GenerateListingResponse(
        title_regional=data.get("title_regional", ""),
        title_english=data.get("title_english", ""),
        description_regional=data.get("description_regional", ""),
        description_english=data.get("description_english", ""),
    )
