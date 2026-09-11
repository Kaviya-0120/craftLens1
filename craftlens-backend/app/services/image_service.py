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
    """Run rembg with isnet-general-use model. Returns PNG bytes."""
    try:
        from rembg import remove, new_session  # type: ignore
    except (ImportError, SystemExit) as e:
        raise RuntimeError(
            "rembg failed to load. Ensure onnxruntime is installed: "
            "pip install onnxruntime"
        ) from e

    logger.info("rembg: removing background (model=isnet-general-use)…")
    # new_session() downloads model weights (~170 MB) on first call — expected
    try:
        session = new_session("isnet-general-use")
        result: bytes = remove(image_bytes, session=session)
    except SystemExit as e:
        raise RuntimeError(
            "rembg exited unexpectedly. This usually means onnxruntime is missing "
            "or the model failed to download. Check server logs."
        ) from e
    logger.info("rembg: background removed (%d bytes out).", len(result))
    return result


def _apply_clahe(image_bytes: bytes) -> bytes:
    """Apply CLAHE lighting correction on the L channel in LAB colour space."""
    import cv2  # type: ignore
    import numpy as np
    from PIL import Image
    import io

    # Decode PNG bytes (may have alpha from rembg)
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

    # Work on the RGB channels only
    rgb = np.array(pil_img.convert("RGB"))

    # Convert to LAB
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)

    # CLAHE on L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_ch)

    # Merge and convert back
    lab_enhanced = cv2.merge([l_enhanced, a_ch, b_ch])
    rgb_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)

    # Re-apply original alpha channel
    alpha = np.array(pil_img.split()[3])
    result_pil = Image.fromarray(rgb_enhanced)
    result_pil.putalpha(Image.fromarray(alpha))

    buf = io.BytesIO()
    result_pil.save(buf, format="PNG")
    return buf.getvalue()


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
