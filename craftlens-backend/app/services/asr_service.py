"""
ASR Service — wraps Whisper (self-hosted) and Bhashini (REST API).

Switch provider via ASR_PROVIDER in .env:
    whisper   — fully local, no API key needed
    bhashini  — Government of India free multilingual ASR

Public interface:
    transcribe(audio_bytes: bytes, filename: str) -> TranscribeResult
"""

from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# ── Whisper model cache (load once, reuse forever) ────────────────────────────
_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper  # lazy import — only needed when ASR_PROVIDER=whisper
        size = settings.whisper_model_size
        logger.info("Loading Whisper model '%s' (one-time download if not cached)…", size)
        _whisper_model = whisper.load_model(size)
        logger.info("Whisper model '%s' loaded.", size)
    return _whisper_model


# ── Result type ────────────────────────────────────────────────────────────────

@dataclass
class TranscribeResult:
    transcript: str
    detected_language: str
    confidence: float  # Whisper always 1.0; Bhashini passes its score


# ── Whisper backend ────────────────────────────────────────────────────────────

def _transcribe_whisper_api(audio_bytes: bytes, filename: str) -> TranscribeResult:
    """Use Groq's Whisper API instead of local model - optimized for free tier"""
    try:
        from groq import Groq
    except ImportError as e:
        raise RuntimeError("groq package not installed. Run: pip install groq") from e

    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set in .env")

    _, ext = os.path.splitext(filename)
    ext = ext.lower() if ext else ".wav"

    # Save audio temporarily for API upload
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        client = Groq(api_key=settings.groq_api_key)
        logger.info("Calling Groq Whisper API on %d bytes (ext=%s)…", len(audio_bytes), ext)
        
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(filename, audio_file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
                language="en"  # or None for auto-detect
            )
        
        transcript = (transcription.text or "").strip()
        language = getattr(transcription, 'language', 'en')
        logger.info("Groq Whisper done — lang=%s  chars=%d", language, len(transcript))
        return TranscribeResult(transcript=transcript, detected_language=language, confidence=1.0)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _transcribe_whisper(audio_bytes: bytes, filename: str) -> TranscribeResult:
    """Fallback to local Whisper (not recommended for free tier)"""
    _, ext = os.path.splitext(filename)
    ext = ext.lower() if ext else ".wav"

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        model = _get_whisper_model()
        logger.info("Running Whisper on %d bytes (ext=%s)…", len(audio_bytes), ext)
        result = model.transcribe(tmp_path, language=None, fp16=False)
        transcript = (result.get("text") or "").strip()
        language = result.get("language") or "unknown"
        logger.info("Whisper done — lang=%s  chars=%d", language, len(transcript))
        return TranscribeResult(transcript=transcript, detected_language=language, confidence=1.0)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ── Bhashini backend ───────────────────────────────────────────────────────────

def _transcribe_bhashini(audio_bytes: bytes, filename: str) -> TranscribeResult:
    """
    Call the Bhashini ASR pipeline.
    API reference: https://bhashini.gov.in/ulca/model/api-integration

    Requires BHASHINI_API_KEY, BHASHINI_USER_ID, BHASHINI_PIPELINE_ID in .env.
    """
    if not settings.bhashini_api_key:
        raise RuntimeError(
            "BHASHINI_API_KEY not set. Add it to .env or switch ASR_PROVIDER=whisper."
        )

    import base64

    audio_b64 = base64.b64encode(audio_bytes).decode()

    # Determine source format
    _, ext = os.path.splitext(filename)
    audio_format = ext.lstrip(".").lower() or "wav"

    headers = {
        "userID": settings.bhashini_user_id,
        "ulcaApiKey": settings.bhashini_api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "pipelineTasks": [
            {
                "taskType": "asr",
                "config": {
                    "language": {"sourceLanguage": ""},  # empty = auto-detect
                    "serviceId": settings.bhashini_pipeline_id,
                    "audioFormat": audio_format,
                    "samplingRate": 16000,
                },
            }
        ],
        "inputData": {
            "audio": [{"audioContent": audio_b64}]
        },
    }

    try:
        resp = httpx.post(
            "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
            json=payload,
            headers=headers,
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        output = data["pipelineResponse"][0]["output"][0]
        transcript = output.get("source", "").strip()
        language = (
            data["pipelineResponse"][0]
            .get("config", {})
            .get("language", {})
            .get("sourceLanguage", "unknown")
        )
        confidence = float(output.get("score", 1.0))
        return TranscribeResult(transcript=transcript, detected_language=language, confidence=confidence)
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Bhashini ASR HTTP error {e.response.status_code}: {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"Bhashini ASR failed: {e}") from e


# ── Public interface ───────────────────────────────────────────────────────────

_ALLOWED_EXTENSIONS = {".webm", ".mp3", ".wav", ".m4a", ".ogg", ".mp4", ".flac"}


def validate_audio_file(filename: str, size_bytes: int) -> None:
    """Raise ValueError with a clear message if the file is invalid."""
    _, ext = os.path.splitext(filename)
    if ext.lower() not in _ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported audio format '{ext}'. "
            f"Allowed: {', '.join(_ALLOWED_EXTENSIONS)}"
        )
    if size_bytes > settings.max_upload_bytes:
        mb = settings.max_upload_bytes // (1024 * 1024)
        raise ValueError(f"File too large — maximum upload size is {mb} MB.")


def transcribe(audio_bytes: bytes, filename: str) -> TranscribeResult:
    """
    Transcribe audio using the configured ASR provider.

    Raises
    ------
    ValueError   : invalid file type or size
    RuntimeError : ASR failure
    """
    validate_audio_file(filename, len(audio_bytes))

    provider = settings.asr_provider.lower()
    if provider == "whisper":
        # Local Whisper (not recommended for free tier - high memory)
        return _transcribe_whisper(audio_bytes, filename)
    elif provider == "groq":
        # Groq Whisper API (recommended for free tier)
        return _transcribe_whisper_api(audio_bytes, filename)
    elif provider == "bhashini":
        return _transcribe_bhashini(audio_bytes, filename)
    else:
        raise RuntimeError(
            f"Unknown ASR_PROVIDER='{provider}'. Supported: whisper, groq, bhashini"
        )
