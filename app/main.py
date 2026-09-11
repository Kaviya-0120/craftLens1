"""
CraftLens — FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.utils.config import settings
from app.models.common import HealthResponse, ErrorResponse

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan: warm up Whisper model at startup ────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once on startup (before the first request) and once on shutdown.
    Pre-loading Whisper here means the first /voice/transcribe call isn't slow.
    """
    logger.info("CraftLens starting up — environment: %s", settings.app_env)
    try:
        from app.services.transcription import get_whisper_model
        get_whisper_model()          # downloads + caches model weights
    except Exception as exc:
        # Don't crash the whole server if Whisper fails to load at startup;
        # the endpoint will surface the error properly when called.
        logger.warning("Whisper pre-load failed (will retry on first request): %s", exc)

    yield  # ← server is live here

    logger.info("CraftLens shutting down.")


# ── App instance ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="CraftLens API",
    description=(
        "Voice-first AI catalogue & pricing assistant for Indian artisans. "
        "Each phase is a standalone REST endpoint — test them in sequence with "
        "the curl examples in the README."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS — open for local dev ─────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Static files (processed images live here) ────────────────────────────────

import os
os.makedirs(settings.static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


# ── Global exception handler — no raw tracebacks to clients ──────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)},
    )


# ── Routers ───────────────────────────────────────────────────────────────────

from app.routers import voice, listing  # noqa: E402  (after app creation)

app.include_router(voice.router)
app.include_router(listing.router)


# ── Health endpoint ───────────────────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
    description="Returns `{ status: ok }` — use this to verify the server is up.",
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")
