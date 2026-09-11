"""
Pricing Service — FAISS-based similarity search against a pre-built product index.

Setup (one-time):
    Run scripts/build_price_index.py to generate:
        data/price_index.faiss   — FAISS IndexFlatL2
        data/price_metadata.csv  — aligned metadata: title, category, price

Public interface:
    estimate_price(fields: dict, listing_text: str) -> dict
"""

from __future__ import annotations

import logging
import statistics
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# ── Embedding model cache ──────────────────────────────────────────────────────
_embedder = None
_faiss_index = None
_metadata_df = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer  # type: ignore
        logger.info("Loading sentence-transformer '%s'…", settings.embedding_model)
        _embedder = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded.")
    return _embedder


def _get_index_and_metadata():
    global _faiss_index, _metadata_df
    if _faiss_index is None or _metadata_df is None:
        import faiss  # type: ignore
        import pandas as pd

        index_path = Path(settings.price_index_path)
        meta_path = Path(settings.price_metadata_path)

        if not index_path.exists() or not meta_path.exists():
            raise RuntimeError(
                "Price index not found. "
                "Run: python scripts/build_price_index.py\n"
                f"Expected:\n  {index_path}\n  {meta_path}"
            )

        logger.info("Loading FAISS index from %s…", index_path)
        _faiss_index = faiss.read_index(str(index_path))
        _metadata_df = pd.read_csv(str(meta_path))
        logger.info(
            "FAISS index loaded: %d vectors. Metadata: %d rows.",
            _faiss_index.ntotal,
            len(_metadata_df),
        )
    return _faiss_index, _metadata_df


def _build_query_text(fields: dict[str, Any], listing_text: str) -> str:
    parts = [listing_text]
    for key in ("material", "craft_technique", "region", "color", "size"):
        val = fields.get(key)
        if val:
            parts.append(str(val))
    return " ".join(parts)


def _keyword_filter(df, fields: dict[str, Any]):
    """
    Cheap keyword pre-filter by material or category.
    Returns filtered DataFrame, or full df if no filter matches.
    """
    import pandas as pd

    keywords = []
    for key in ("material", "craft_technique", "region"):
        val = fields.get(key)
        if val:
            keywords.extend(str(val).lower().split())

    if not keywords:
        return df, False  # (df, was_filtered)

    mask = pd.Series([False] * len(df), index=df.index)
    for kw in keywords:
        if "category" in df.columns:
            mask |= df["category"].str.lower().str.contains(kw, na=False)
        if "title" in df.columns:
            mask |= df["title"].str.lower().str.contains(kw, na=False)

    filtered = df[mask]
    if len(filtered) < 3:
        # Too few after filtering — fall back to full index
        return df, False
    return filtered, True


def estimate_price(fields: dict[str, Any], listing_text: str) -> dict[str, Any]:
    """
    Embed the listing, search FAISS for top-k comparables, return price stats.

    Returns dict matching PricingEstimateResponse schema.
    """
    import faiss
    import numpy as np

    index, meta_df = _get_index_and_metadata()
    embedder = _get_embedder()

    query_text = _build_query_text(fields, listing_text)
    filtered_df, was_filtered = _keyword_filter(meta_df, fields)

    top_k = settings.pricing_top_k
    low_confidence = False

    # If filtered, build a sub-index from the filtered rows
    if was_filtered:
        sub_indices = filtered_df.index.tolist()
        # Retrieve vectors for sub-set from the full index
        # FAISS IndexFlatL2 doesn't support direct sub-indexing;
        # we search full index then filter results
        query_vec = embedder.encode([query_text], normalize_embeddings=True).astype("float32")
        distances, idx_arr = index.search(query_vec, top_k * 3)  # over-fetch
        flat_idx = idx_arr[0].tolist()
        # Keep only those in the filtered set
        keep = [i for i in flat_idx if i in sub_indices and i >= 0][:top_k]
        if len(keep) < 3:
            # Relax to full search
            keep = [i for i in flat_idx if i >= 0][:top_k]
            low_confidence = True
    else:
        query_vec = embedder.encode([query_text], normalize_embeddings=True).astype("float32")
        distances, idx_arr = index.search(query_vec, top_k)
        keep = [i for i in idx_arr[0].tolist() if i >= 0]

    if len(keep) < 3:
        low_confidence = True

    rows = meta_df.iloc[keep]
    prices = rows["price"].dropna().tolist()

    if not prices:
        return {
            "price_range": [0.0, 0.0],
            "median_price": 0.0,
            "comparable_count": 0,
            "comparable_samples": [],
            "low_confidence": True,
        }

    samples = []
    for _, row in rows.iterrows():
        samples.append({
            "title": str(row.get("title", "")),
            "price": float(row.get("price", 0)),
            "category": str(row.get("category", "")),
        })

    return {
        "price_range": [round(min(prices), 2), round(max(prices), 2)],
        "median_price": round(statistics.median(prices), 2),
        "comparable_count": len(prices),
        "comparable_samples": samples[:5],  # cap at 5 for response size
        "low_confidence": low_confidence,
    }
