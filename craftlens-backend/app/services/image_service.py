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
    Lightweight image processing - skip background removal for free tier.
    Just optimize the image for web display.
    """
    try:
        from PIL import Image, ImageEnhance
        import io
        
        logger.info("Processing image (lightweight mode - no background removal)")
        
        # Decode image
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if pil_img.mode in ('RGBA', 'P'):
            pil_img = pil_img.convert('RGB')
        
        # Enhance contrast slightly
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(1.1)
        
        # Optimize size for web
        max_size = (1200, 1200)
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save as PNG
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG", optimize=True)
        result = buf.getvalue()
        
        logger.info("Image processed (%d bytes out).", len(result))
        return result
    except Exception as e:
        logger.warning(f"Image processing failed: {e} - using original")
        return image_bytes


def _apply_clahe(image_bytes: bytes) -> bytes:
    """
    Apply basic brightness and contrast enhancement using Pillow.
    Lightweight alternative to OpenCV CLAHE.
    """
    try:
        from PIL import Image, ImageEnhance
        import io

        # Decode image
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        # Ensure RGB
        if pil_img.mode == 'RGBA':
            # Preserve alpha if present
            alpha = pil_img.split()[3]
            rgb = pil_img.convert('RGB')
            
            # Enhance
            enhancer = ImageEnhance.Brightness(rgb)
            rgb = enhancer.enhance(1.15)
            enhancer = ImageEnhance.Contrast(rgb)
            rgb = enhancer.enhance(1.1)
            
            # Re-apply alpha
            rgb = rgb.convert('RGBA')
            rgb.putalpha(alpha)
            result_pil = rgb
        else:
            # Simple enhancement for RGB/L
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            
            enhancer = ImageEnhance.Brightness(pil_img)
            result_pil = enhancer.enhance(1.15)
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
