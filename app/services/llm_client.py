"""
Thin wrapper around the configured LLM provider (Groq by default).

Adding a new provider = add a branch in `chat_completion()`.
The rest of the codebase never imports the Groq SDK directly.
"""

from __future__ import annotations

import logging
from typing import Any

from app.utils.config import settings

logger = logging.getLogger(__name__)


def _get_groq_client():
    """Lazy import so the app starts even if groq isn't installed yet."""
    try:
        from groq import Groq  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "groq package not installed. Run: pip install groq"
        ) from e

    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file."
        )
    return Groq(api_key=settings.groq_api_key)


def chat_completion(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """
    Send a chat completion request to the configured LLM provider.

    Returns the assistant message content as a plain string.

    Raises
    ------
    RuntimeError  on API or configuration failure.
    """
    provider = settings.llm_provider.lower()
    model = settings.llm_model

    logger.info("LLM call  provider=%s  model=%s", provider, model)

    try:
        if provider == "groq":
            client = _get_groq_client()
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content: str = response.choices[0].message.content or ""
            logger.info("LLM response received (%d chars).", len(content))
            return content

        else:
            raise RuntimeError(
                f"Unsupported LLM_PROVIDER='{provider}'. "
                "Currently supported: groq"
            )

    except RuntimeError:
        raise
    except Exception as exc:
        logger.exception("LLM call failed: %s", exc)
        raise RuntimeError(f"LLM request failed: {exc}") from exc
