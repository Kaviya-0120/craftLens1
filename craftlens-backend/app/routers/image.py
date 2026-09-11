"""
Image Router — Phase 3 & 6 (CLIP tagging)

  POST /image/process   upload → background removal + CLAHE → saved PNG
  POST /image/tag       image_id → CLIP visual labels
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.models.schemas import ImageTagRequest, ImageTagResponse, ProcessImageResponse, VisualTag
from app.services import image_service, clip_service
from app.utils.errors import craft_error_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/image", tags=["Image Pipeline"])


# ─────────────────────────────────────────────────────────────────────────────
# POST /image/process
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/process",
    response_model=ProcessImageResponse,
    summary="Remove background and correct lighting",
    description=(
        "Upload a JPG/PNG/WebP image. "
        "Runs rembg (isnet-general-use) for background removal, "
        "then OpenCV CLAHE for lighting correction. "
        "Saves result to /static/{uuid}.png and returns the URL."
    ),
)
async def process_image(
    file: Annotated[UploadFile, File(description="Image file — jpg, png, or webp")],
):
    if not file or not file.filename:
        return craft_error_response(400, "No image file provided.")

    image_bytes = await file.read()
    if not image_bytes:
        return craft_error_response(400, "Uploaded image file is empty.")

    try:
        result = image_service.process_image(image_bytes, file.filename)
        return ProcessImageResponse(
            processed_image_url=result.processed_image_url,
            image_id=result.image_id,
        )
    except ValueError as exc:
        return craft_error_response(422, str(exc), exc, log_traceback=False)
    except RuntimeError as exc:
        return craft_error_response(500, "Image processing failed.", exc)
    except Exception as exc:
        return craft_error_response(500, "Unexpected error during image processing.", exc)


# ─────────────────────────────────────────────────────────────────────────────
# POST /image/tag
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/tag",
    response_model=ImageTagResponse,
    summary="Tag a processed image with CLIP visual labels",
    description=(
        "Pass the image_id from /image/process. "
        "Runs CLIP (ViT-B-32) zero-shot classification against a textile/craft label set. "
        "Returns top-3 labels with confidence scores."
    ),
)
async def tag_image(body: ImageTagRequest):
    try:
        tags = clip_service.tag_image(body.image_id)
        return ImageTagResponse(
            visual_tags=[VisualTag(label=t["label"], score=t["score"]) for t in tags]
        )
    except FileNotFoundError as exc:
        return craft_error_response(404, str(exc), exc, log_traceback=False)
    except RuntimeError as exc:
        return craft_error_response(500, "CLIP inference failed.", exc)
    except Exception as exc:
        return craft_error_response(500, "Unexpected error during image tagging.", exc)
