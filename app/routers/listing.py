"""
Listing router — Phase 1, step 3.

  POST /listing/generate  — structured fields + transcript → bilingual listing
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.listing import GenerateListingRequest, GenerateListingResponse
from app.models.common import ErrorResponse
from app.services.listing_generation import generate_listing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/listing", tags=["Listing Generation"])


@router.post(
    "/generate",
    response_model=GenerateListingResponse,
    responses={
        422: {"model": ErrorResponse, "description": "LLM returned unparseable JSON"},
        500: {"model": ErrorResponse, "description": "LLM call failed"},
    },
    summary="Generate a bilingual e-commerce listing",
    description=(
        "Accepts the structured fields from /voice/extract-fields plus "
        "the original transcript. Returns SEO-friendly title and description "
        "in both English and the artisan's regional language."
    ),
)
async def generate_listing_endpoint(body: GenerateListingRequest) -> GenerateListingResponse:
    try:
        result = await generate_listing(
            structured_fields=body.structured_fields.model_dump(),
            transcript=body.transcript,
        )
        return GenerateListingResponse(**result)

    except ValueError as exc:
        logger.warning("JSON parse error in /listing/generate: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except RuntimeError as exc:
        logger.error("LLM error in /listing/generate: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error in /listing/generate")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {exc}",
        )
