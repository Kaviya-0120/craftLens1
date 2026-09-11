"""
Standard error response helpers.

Every router uses `craft_error_response()` so clients always see:
    { "error": true, "message": "...", "detail": "..." }

Never let raw Python tracebacks reach the client; log them server-side.
"""

from __future__ import annotations

import logging
import traceback

from fastapi import HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def craft_error_response(
    status_code: int,
    message: str,
    exc: Exception | None = None,
    log_traceback: bool = True,
) -> JSONResponse:
    """
    Build a standard error JSONResponse.

    Parameters
    ----------
    status_code   : HTTP status code to return
    message       : human-readable summary (safe to show the client)
    exc           : original exception (logged server-side, NOT exposed to client)
    log_traceback : whether to log the full traceback (default True)
    """
    detail: str | None = None
    if exc is not None:
        detail = str(exc)
        if log_traceback:
            logger.error(
                "Error %d — %s\n%s",
                status_code,
                message,
                traceback.format_exc(),
            )
        else:
            logger.warning("Error %d — %s: %s", status_code, message, exc)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "message": message,
            "detail": detail,
        },
    )


def raise_http(status_code: int, message: str, exc: Exception | None = None) -> None:
    """
    Log and raise an HTTPException with the standard error body.
    Use this inside router functions where FastAPI's exception handling
    will convert it to a response automatically.
    """
    if exc is not None:
        logger.error(
            "HTTP %d — %s\n%s", status_code, message, traceback.format_exc()
        )
    raise HTTPException(
        status_code=status_code,
        detail={"error": True, "message": message, "detail": str(exc) if exc else None},
    )
