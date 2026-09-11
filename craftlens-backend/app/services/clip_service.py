"""
CLIP Service — visual tagging using open_clip (ViT-B-32).

Public interface:
    tag_image(image_id: str) -> list[dict]  — top-3 labels with scores
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# ── Candidate label set for Indian textiles / crafts ─────────────────────────
CANDIDATE_LABELS = [
    "silk fabric",
    "cotton fabric",
    "wool fabric",
    "jute fabric",
    "handloom weave",
    "block print textile",
    "zari embroidery",
    "hand embroidery",
    "tie-dye fabric",
    "ikat weave",
    "leather craft",
    "terracotta pottery",
    "brass metalwork",
    "wood carving",
    "cane and bamboo craft",
    "stone carving",
    "blue pottery",
    "warli painting",
    "madhubani painting",
    "jewelry",
]

# ── Model cache ────────────────────────────────────────────────────────────────
_clip_model = None
_clip_preprocess = None
_clip_tokenizer = None


def _get_clip_model():
    global _clip_model, _clip_preprocess, _clip_tokenizer
    if _clip_model is None:
        try:
            import open_clip  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "open_clip_torch not installed. Run: pip install open-clip-torch"
            ) from e

        logger.info("Loading CLIP model ViT-B-32 (one-time download if not cached)…")
        _clip_model, _, _clip_preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="openai"
        )
        _clip_tokenizer = open_clip.get_tokenizer("ViT-B-32")
        _clip_model.eval()
        logger.info("CLIP model loaded.")
    return _clip_model, _clip_preprocess, _clip_tokenizer


def tag_image(image_id: str, top_k: int = 3) -> list[dict[str, Any]]:
    """
    Run CLIP zero-shot classification on a processed image.

    Parameters
    ----------
    image_id : UUID string matching a file in static_dir
    top_k    : number of top labels to return

    Returns
    -------
    list of {"label": str, "score": float} sorted by score desc

    Raises
    ------
    FileNotFoundError : image_id not found in static dir
    RuntimeError      : CLIP inference failure
    """
    import torch
    from PIL import Image

    # Locate image
    static_dir = Path(settings.static_dir)
    image_path = static_dir / f"{image_id}.png"
    if not image_path.exists():
        raise FileNotFoundError(
            f"Image '{image_id}' not found in {settings.static_dir}. "
            "Call /image/process first."
        )

    try:
        model, preprocess, tokenizer = _get_clip_model()

        image = preprocess(Image.open(image_path)).unsqueeze(0)
        text_tokens = tokenizer(CANDIDATE_LABELS)

        with torch.no_grad():
            image_features = model.encode_image(image)
            text_features = model.encode_text(text_tokens)

            # Normalise for cosine similarity
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

        scores = similarity[0].tolist()
        ranked = sorted(
            zip(CANDIDATE_LABELS, scores), key=lambda x: x[1], reverse=True
        )

        result = [{"label": lbl, "score": round(sc, 4)} for lbl, sc in ranked[:top_k]]
        logger.info("CLIP tags for %s: %s", image_id, result)
        return result

    except FileNotFoundError:
        raise
    except Exception as exc:
        raise RuntimeError(f"CLIP inference failed: {exc}") from exc
