"""
Build Price Index — one-time setup script for Phase 5 (Pricing Engine).

Usage:
    python scripts/build_price_index.py

What it does:
    1. Loads a Kaggle product CSV from ./data/
    2. Cleans and normalises data
    3. Embeds (title + description) with sentence-transformers all-MiniLM-L6-v2
    4. Builds a FAISS IndexFlatL2 and saves it to PRICE_INDEX_PATH
    5. Saves aligned metadata CSV to PRICE_METADATA_PATH

Expected CSV file:
    Place one of these in the ./data/ directory:
      - flipkart_com-ecommerce_sample.csv  (Kaggle: "Flipkart Products")
        Required columns: product_name, description, product_category_tree, retail_price
      - amazon_products.csv  (Kaggle: "Amazon India Products")
        Required columns: product_name, about_product, category, discounted_price

    The script auto-detects the column names listed above.

Run time:
    ~5–15 minutes for 15k–20k rows on a laptop (CPU).
    Subsequent runs re-use cached sentence-transformer weights.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app.config import settings

# ── Column name mappings ────────────────────────────────────────────────────

# Each inner dict maps our canonical names → possible CSV column names
COLUMN_ALIASES = {
    "title": ["product_name", "name", "title", "product_title"],
    "description": ["description", "about_product", "product_description", "highlights"],
    "category": ["product_category_tree", "category", "main_category", "sub_category"],
    "price": ["retail_price", "discounted_price", "actual_price", "selling_price", "price"],
}


def detect_columns(df: pd.DataFrame) -> dict[str, str]:
    """Map canonical names to actual column names present in the DataFrame."""
    cols = {c.lower().strip(): c for c in df.columns}
    mapping = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in cols:
                mapping[canonical] = cols[alias.lower()]
                break
        if canonical not in mapping:
            raise ValueError(
                f"Could not find a column for '{canonical}'. "
                f"DataFrame columns: {list(df.columns)}"
            )
    return mapping


def normalise_price(series: pd.Series) -> pd.Series:
    """Strip currency symbols, commas, ranges; return numeric series."""
    s = series.astype(str)
    # Take first number if range like "500-1000"
    s = s.str.extract(r"(\d[\d,.]*)")[0]
    s = s.str.replace(",", "", regex=False)
    return pd.to_numeric(s, errors="coerce")


def find_csv() -> Path:
    data_dir = Path("./data")
    candidates = list(data_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(
            "No CSV file found in ./data/\n"
            "Download a Flipkart or Amazon India products dataset from Kaggle "
            "and place it in ./data/"
        )
    if len(candidates) > 1:
        print(f"Multiple CSVs found: {[c.name for c in candidates]}")
        print(f"Using: {candidates[0].name}")
    return candidates[0]


def main():
    print("=" * 60)
    print("CraftLens — Building Price Index")
    print("=" * 60)

    # 1. Load CSV
    csv_path = find_csv()
    print(f"\n[1/5] Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path, on_bad_lines="skip", low_memory=False)
    print(f"      Raw rows: {len(df):,}")

    # 2. Detect and normalise columns
    print("[2/5] Detecting columns…")
    col_map = detect_columns(df)
    print(f"      Column mapping: {col_map}")

    df = df.rename(columns={v: k for k, v in col_map.items()})
    df = df[["title", "description", "category", "price"]].copy()

    # Normalise price
    df["price"] = normalise_price(df["price"])

    # Clean
    df = df.dropna(subset=["title", "price"])
    df = df[df["price"] > 0]
    df["description"] = df["description"].fillna("")
    df["category"] = df["category"].fillna("general")
    df = df.drop_duplicates(subset=["title"])
    df = df.reset_index(drop=True)
    print(f"      Clean rows: {len(df):,}")

    # 3. Build embed text
    print("[3/5] Building embed texts (title + description)…")
    df["embed_text"] = (
        df["title"].str.strip() + " " + df["description"].str[:300].str.strip()
    )

    # 4. Embed
    print(f"[4/5] Embedding with '{settings.embedding_model}'…")
    print("      This may take several minutes on CPU…")
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(settings.embedding_model)
    embeddings = model.encode(
        df["embed_text"].tolist(),
        batch_size=256,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")
    print(f"      Embeddings shape: {embeddings.shape}")

    # 5. Build and save FAISS index
    print("[5/5] Building FAISS index…")
    import faiss

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product on normalised vectors = cosine sim
    index.add(embeddings)

    index_path = Path(settings.price_index_path)
    meta_path = Path(settings.price_metadata_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(index_path))
    print(f"      FAISS index saved: {index_path}  ({index.ntotal:,} vectors)")

    # Save metadata
    meta_df = df[["title", "category", "price"]].copy()
    meta_df.to_csv(str(meta_path), index=False)
    print(f"      Metadata saved:    {meta_path}  ({len(meta_df):,} rows)")

    print("\n✓ Price index built successfully.")
    print(f"  Index:    {index_path}")
    print(f"  Metadata: {meta_path}")
    print("\nYou can now start the server and use POST /pricing/estimate")


if __name__ == "__main__":
    main()
