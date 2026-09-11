"""
CraftLens — FastAPI application entry point.

Start the server:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Interactive API docs:
    http://localhost:8000/docs
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup tasks (run before first request):
    - Ensure static dir exists
    - Initialise SQLite schema
    - Pre-load Whisper model (if ASR_PROVIDER=whisper) so first request isn't slow
    """
    logger.info("CraftLens starting — env=%s", settings.app_env)

    # Static dir
    os.makedirs(settings.static_dir, exist_ok=True)

    # DB schema
    try:
        from app.services.db_service import init_db
        init_db()
    except Exception as exc:
        logger.warning("DB init warning (non-fatal): %s", exc)

    # Whisper pre-load
    if settings.asr_provider.lower() == "whisper":
        try:
            from app.services.asr_service import _get_whisper_model
            _get_whisper_model()
        except Exception as exc:
            logger.warning(
                "Whisper pre-load failed — will retry on first request: %s", exc
            )

    logger.info("CraftLens ready.")
    yield
    logger.info("CraftLens shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CraftLens API",
    description=(
        "Voice-first AI catalogue and pricing assistant for Indian artisans.\n\n"
        "Test each phase in order using the curl examples in README.md, "
        "or explore interactively below."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — open for local dev ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to specific origins before any deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files ──────────────────────────────────────────────────────────────
app.mount(
    "/static",
    StaticFiles(directory=settings.static_dir),
    name="static",
)

# ── Global exception handler — never leak raw tracebacks ──────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An unexpected internal error occurred.",
            "detail": str(exc),
        },
    )


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"], summary="Health check")
async def health():
    return {"status": "ok"}


# ── Routers ───────────────────────────────────────────────────────────────────
from app.routers import voice, image, listing, pricing, consistency, catalogue  # noqa: E402

app.include_router(voice.router)
app.include_router(image.router)
app.include_router(listing.router)
app.include_router(pricing.router)
app.include_router(consistency.router)
app.include_router(catalogue.router)
