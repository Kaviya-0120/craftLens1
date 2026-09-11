"""
Shared error and health schemas used across all routers.
"""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Short error type / code")
    detail: str = Field(..., description="Human-readable description of what went wrong")


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
