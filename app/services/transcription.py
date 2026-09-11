"""
Transcription service — wraps openai-whisper (self-hosted).

The Whisper model is loaded once at startup and cached in module-level state
so repeated calls don't reload it from disk on every request.
"""

from __future__ import annotations

import os
import tempfile
import logging
from functools import lru_cache
from typing import BinaryIO

import whisper

from app.utils.config import settings

logger = logging.getLogger(__name__)

# ── Model cache ──────────────────────────────────────────────────────────────

_whisper_model: whisper.Whisper | None = None


def get_whisper_model() -> whisper.Whisper:
    """
    Lazy-load the Whisper model once and keep it in memory.
    Thread-safe enough for a single-worker dev server; for production
    you'd want a proper singleton lock.
    """
    global _whisper_model
    if _whisper_model is None:
        model_name = settings.whisper_model  # e.g. "base" or "small"
        logger.info("Loading Whisper model '%s' — this may take a moment …", model_name)
        _whisper_model = whisper.load_model(model_name)
        logger.info("Whisper model '%s' loaded.", model_name)
    return _whisper_model


# ── Core service function ─────────────────────────────────────────────────────

async def transcribe_audio(file_bytes: bytes, original_filename: str) -> dict:
    """
    Write audio bytes to a temp file, run Whisper, return transcript + language.

    Parameters
    ----------
    file_bytes        : raw bytes from the uploaded audio file
    original_filename : used only to infer the file extension for the temp file

    Returns
    -------
    {
        "transcript": str,
        "detected_language": str  # ISO 639-1, e.g. "hi", "en"
    }

    Raises
    ------
    RuntimeError  on Whisper failure (caller converts to HTTP 500)
    """
    # Determine file extension so ffmpeg inside Whisper can identify the codec
    _, ext = os.path.splitext(original_filename)
    ext = ext.lower() if ext else ".wav"

    # Write to a named temp file — Whisper needs a real file path, not a stream
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        model = get_whisper_model()
        logger.info("Running Whisper transcription on '%s' …", tmp_path)

        # language=None → auto-detect
        result = model.transcribe(tmp_path, language=None, fp16=False)

        transcript: str = result.get("text", "").strip()
        detected_language: str = result.get("language", "unknown")

        logger.info(
            "Transcription complete. Language: %s  |  Length: %d chars",
            detected_language,
            len(transcript),
        )
        return {"transcript": transcript, "detected_language": detected_language}

    except Exception as exc:
        logger.exception("Whisper transcription failed: %s", exc)
        raise RuntimeError(f"Transcription failed: {exc}") from exc

    finally:
        # Always clean up the temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
