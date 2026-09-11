"""
LLM Service — unified interface to Groq, Gemini, and Ollama.

Public interface:
    call_llm(system_prompt, user_prompt, json_mode=True) -> str

Every router/service calls this single function.
Switch provider via LLM_PROVIDER in .env — no code changes needed.

JSON parsing utility:
    parse_llm_json(text) -> dict  — strips markdown fences, retries once
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# ── Prompt file loader ────────────────────────────────────────────────────────

_PROMPT_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from app/prompts/<name>.txt"""
    path = _PROMPT_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8").strip()


# ── Provider implementations ──────────────────────────────────────────────────

def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    try:
        from groq import Groq  # type: ignore
    except ImportError as e:
        raise RuntimeError("groq package not installed. Run: pip install groq") from e

    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set in .env")

    client = Groq(api_key=settings.groq_api_key)

    kwargs: dict[str, Any] = dict(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    # Groq supports response_format for JSON mode
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    return (resp.choices[0].message.content or "").strip()


def _call_gemini(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "google-generativeai package not installed. Run: pip install google-generativeai"
        ) from e

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=system_prompt,
    )

    generation_config = {}
    if json_mode:
        generation_config["response_mime_type"] = "application/json"

    resp = model.generate_content(user_prompt, generation_config=generation_config or None)
    return (resp.text or "").strip()


def _call_ollama(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    import httpx  # already in requirements

    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    if json_mode:
        payload["format"] = "json"

    try:
        resp = httpx.post(
            f"{settings.ollama_base_url}/api/chat",
            json=payload,
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return (data.get("message", {}).get("content") or "").strip()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Ollama HTTP error {e.response.status_code}: {e.response.text}"
        ) from e
    except httpx.ConnectError as e:
        raise RuntimeError(
            f"Cannot connect to Ollama at {settings.ollama_base_url}. "
            "Is `ollama serve` running?"
        ) from e


# ── JSON extraction ───────────────────────────────────────────────────────────

def parse_llm_json(text: str) -> dict[str, Any]:
    """
    Extract a JSON object from an LLM response string.

    Strategy:
    1. Strip markdown fences.
    2. Try direct json.loads.
    3. Regex-find the first {...} block.

    Raises ValueError if nothing parses.
    """
    # Strip fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"LLM response did not contain valid JSON.\nRaw: {text[:500]}")


# ── Public interface ──────────────────────────────────────────────────────────

def call_llm(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = True,
) -> str:
    """
    Send a chat completion to the configured LLM provider.

    Parameters
    ----------
    system_prompt : system/instruction message
    user_prompt   : user/input message
    json_mode     : hint to provider to return valid JSON (provider-specific)

    Returns
    -------
    Raw response string from the model.

    Raises
    ------
    RuntimeError on API / configuration failure.
    """
    provider = settings.llm_provider.lower()
    logger.info("LLM call — provider=%s  json_mode=%s", provider, json_mode)

    try:
        if provider == "groq":
            return _call_groq(system_prompt, user_prompt, json_mode)
        elif provider == "gemini":
            return _call_gemini(system_prompt, user_prompt, json_mode)
        elif provider == "ollama":
            return _call_ollama(system_prompt, user_prompt, json_mode)
        else:
            raise RuntimeError(
                f"Unknown LLM_PROVIDER='{provider}'. Supported: groq, gemini, ollama"
            )
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc
