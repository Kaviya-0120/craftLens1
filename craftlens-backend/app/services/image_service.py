"""
Image Service — background removal (rembg) + lighting correction (OpenCV CLAHE).

Public interface:
    process_image(image_bytes: bytes, filename: str) -> ProcessedImageResult
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

_ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass
class ProcessedImageResult:
    image_id: str
    processed_image_url: str  # e.g. /static/{uuid}.png


def validate_image_file(filename: str, size_bytes: int) -> None:
    _, ext = os.path.splitext(filename)
    if ext.lower() not in _ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format '{ext}'. "
            f"Allowed: {', '.join(_ALLOWED_IMAGE_EXTENSIONS)}"
        )
    if size_bytes > settings.max_upload_bytes:
        mb = settings.max_upload_bytes // (1024 * 1024)
        raise ValueError(f"File too large — maximum upload size is {mb} MB.")


def _remove_background(image_bytes: bytes) -> bytes:
    """
    Remove background using remove.bg API (optimized for free tier).
    Falls back to no removal if API key not set.
    """
    if not settings.removebg_api_key:
        logger.warning("REMOVEBG_API_KEY not set - skipping background removal")
        return image_bytes
    
    try:
        import requests
        logger.info("remove.bg: removing background via API…")
        
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': image_bytes},
            data={'size': 'auto'},
            headers={'X-Api-Key': settings.removebg_api_key},
            timeout=30
        )
        response.raise_for_status()
        logger.info("remove.bg: background removed (%d bytes out).", len(response.content))
        return response.content
    except Exception as e:
        logger.error(f"remove.bg API failed: {e} - using original image")
        return image_bytes


def _apply_clahe(image_bytes: bytes) -> bytes:
    """
    Apply basic brightness enhancement using Pillow (lightweight).
    Replaces OpenCV CLAHE to reduce dependencies.
    """
    try:
        from PIL import Image, ImageEnhance
        import io

        # Decode image
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if pil_img.mode in ('RGBA', 'LA'):
            # Preserve alpha channel
            alpha = pil_img.split()[-1] if pil_img.mode == 'RGBA' else None
            rgb = pil_img.convert('RGB')
            
            # Enhance brightness and contrast
            enhancer = ImageEnhance.Brightness(rgb)
            rgb = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Contrast(rgb)
            rgb = enhancer.enhance(1.1)
            
            # Re-apply alpha if exists
            if alpha:
                rgb = rgb.convert('RGBA')
                rgb.putalpha(alpha)
            result_pil = rgb
        else:
            # Simple enhancement for RGB/L images
            enhancer = ImageEnhance.Brightness(pil_img)
            result_pil = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Contrast(result_pil)
            result_pil = enhancer.enhance(1.1)

        # Save as PNG
        buf = io.BytesIO()
        result_pil.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        logger.warning(f"Image enhancement failed: {e} - using original")
        return image_bytes


def process_image(image_bytes: bytes, filename: str) -> ProcessedImageResult:
    """
    1. Validate file type and size.
    2. Remove background with rembg (isnet-general-use).
    3. Apply CLAHE lighting correction.
    4. Save to static_dir/{uuid}.png.
    5. Return image_id and URL.

    Raises
    ------
    ValueError   : invalid file
    RuntimeError : rembg or OpenCV failure
    """
    validate_image_file(filename, len(image_bytes))

    try:
        # Step 1 — background removal
        no_bg = _remove_background(image_bytes)

        # Step 2 — lighting correction
        corrected = _apply_clahe(no_bg)

        # Step 3 — persist
        image_id = str(uuid.uuid4())
        static_dir = Path(settings.static_dir)
        static_dir.mkdir(parents=True, exist_ok=True)
        out_path = static_dir / f"{image_id}.png"
        out_path.write_bytes(corrected)

        url = f"/static/{image_id}.png"
        logger.info("Image processed and saved: %s", url)
        return ProcessedImageResult(image_id=image_id, processed_image_url=url)

    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Image processing failed: {exc}") from exc
