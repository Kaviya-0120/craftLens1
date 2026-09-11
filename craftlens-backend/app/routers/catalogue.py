"""
Catalogue Router — Phase 8

  POST /catalogue/publish   persist final listing to SQLite
  GET  /listing/{id}        retrieve a published listing (shareable URL)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from app.models.schemas import ListingRecord, PublishRequest, PublishResponse
from app.services import db_service
from app.utils.errors import craft_error_response

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Catalogue"])


# ─────────────────────────────────────────────────────────────────────────────
# POST /catalogue/publish
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/catalogue/publish",
    response_model=PublishResponse,
    summary="Publish a finalised listing to the catalogue",
    description=(
        "Persists the listing to SQLite. "
        "Returns a listing_id and a shareable /listing/{id} URL."
    ),
)
async def publish_listing(body: PublishRequest):
    try:
        listing_id = db_service.create_listing(
            {
                "image_url": body.image_url,
                "title_regional": body.title_regional,
                "title_english": body.title_english,
                "description_regional": body.description_regional,
                "description_english": body.description_english,
                "price": body.price,
                "fields": body.fields.model_dump(),
            }
        )
        return PublishResponse(
            listing_id=listing_id,
            share_url=f"/listing/{listing_id}",
        )
    except Exception as exc:
        return craft_error_response(500, "Failed to publish listing.", exc)


# ─────────────────────────────────────────────────────────────────────────────
# GET /listing/{id}
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/listing/{listing_id}",
    response_model=ListingRecord,
    summary="Retrieve a published listing",
    description=(
        "Returns the full stored listing record as JSON. "
        "This is the shareable/QR-ready endpoint — no frontend required to demo."
    ),
)
async def get_listing(listing_id: str):
    try:
        record = db_service.get_listing(listing_id)
    except Exception as exc:
        return craft_error_response(500, "Database read failed.", exc)

    if record is None:
        return craft_error_response(404, f"Listing '{listing_id}' not found.", log_traceback=False)

    return ListingRecord(**record)
