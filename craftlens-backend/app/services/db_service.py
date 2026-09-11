"""
Database Service — SQLite persistence via SQLAlchemy (sync core).

Table: listings
  id                TEXT PRIMARY KEY  (UUID)
  image_url         TEXT
  title_regional    TEXT
  title_english     TEXT
  description_regional TEXT
  description_english  TEXT
  price             REAL
  fields            TEXT   (JSON string)
  created_at        TEXT   (ISO 8601)

Public interface:
    init_db()                           — called at startup
    create_listing(data: dict) -> str   — returns new listing id
    get_listing(id: str) -> dict|None
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, MetaData, String, Float, Text, Table, create_engine, select
from sqlalchemy.engine import Engine

from app.config import settings

logger = logging.getLogger(__name__)

_engine: Engine | None = None
_metadata = MetaData()

listings_table = Table(
    "listings",
    _metadata,
    Column("id", String, primary_key=True),
    Column("image_url", Text, nullable=False),
    Column("title_regional", Text, nullable=False),
    Column("title_english", Text, nullable=False),
    Column("description_regional", Text, nullable=False),
    Column("description_english", Text, nullable=False),
    Column("price", Float, nullable=False),
    Column("fields", Text, nullable=False),   # JSON string
    Column("created_at", String, nullable=False),
)


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        # For SQLite file paths, convert sqlite:// → sqlite:///
        db_url = settings.database_url
        _engine = create_engine(db_url, connect_args={"check_same_thread": False})
    return _engine


def init_db() -> None:
    """Create tables if they don't exist. Call once at startup."""
    engine = _get_engine()
    _metadata.create_all(engine)
    logger.info("Database initialised: %s", settings.database_url)


def create_listing(data: dict[str, Any]) -> str:
    """
    Insert a new listing row.

    Parameters
    ----------
    data : dict with keys matching the listings_table columns
           (id and created_at auto-generated if absent)

    Returns
    -------
    The new listing's UUID string.
    """
    engine = _get_engine()
    listing_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "id": listing_id,
        "image_url": data["image_url"],
        "title_regional": data["title_regional"],
        "title_english": data["title_english"],
        "description_regional": data["description_regional"],
        "description_english": data["description_english"],
        "price": float(data["price"]),
        "fields": json.dumps(data.get("fields", {})),
        "created_at": now,
    }

    with engine.begin() as conn:
        conn.execute(listings_table.insert().values(**row))

    logger.info("Listing created: %s", listing_id)
    return listing_id


def get_listing(listing_id: str) -> dict[str, Any] | None:
    """Fetch a listing by ID. Returns None if not found."""
    engine = _get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            select(listings_table).where(listings_table.c.id == listing_id)
        ).fetchone()

    if result is None:
        return None

    row = dict(result._mapping)
    # Deserialise fields JSON string back to dict
    row["fields"] = json.loads(row.get("fields") or "{}")
    return row
