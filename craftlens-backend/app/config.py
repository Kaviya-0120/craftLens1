"""
Central application settings loaded from environment / .env file.

Import the `settings` singleton everywhere — never read os.environ directly.

    from app.config import settings
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file (project root), not the working directory.
# This means `uvicorn app.main:app` works correctly regardless of which
# directory it's launched from.
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────
    llm_provider: str = Field(default="groq", alias="LLM_PROVIDER")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="qwen/qwen3.8-27b", alias="GROQ_MODEL")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")

    # ── ASR ──────────────────────────────────────────────────
    asr_provider: str = Field(default="whisper", alias="ASR_PROVIDER")
    whisper_model_size: str = Field(default="base", alias="WHISPER_MODEL_SIZE")

    bhashini_api_key: str = Field(default="", alias="BHASHINI_API_KEY")
    bhashini_user_id: str = Field(default="", alias="BHASHINI_USER_ID")
    bhashini_pipeline_id: str = Field(default="", alias="BHASHINI_PIPELINE_ID")

    # ── Pricing / FAISS ──────────────────────────────────────
    price_index_path: str = Field(default="./data/price_index.faiss", alias="PRICE_INDEX_PATH")
    price_metadata_path: str = Field(default="./data/price_metadata.csv", alias="PRICE_METADATA_PATH")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    pricing_top_k: int = Field(default=10, alias="PRICING_TOP_K")

    # ── Thresholds ───────────────────────────────────────────
    confidence_threshold: float = Field(default=0.7, alias="CONFIDENCE_THRESHOLD")
    consistency_threshold: float = Field(default=0.4, alias="CONSISTENCY_THRESHOLD")

    # ── Persistence ──────────────────────────────────────────
    database_url: str = Field(default="sqlite:///./craftlens.db", alias="DATABASE_URL")

    # ── App ──────────────────────────────────────────────────
    app_env: str = Field(default="development", alias="APP_ENV")
    static_dir: str = Field(default="./static", alias="STATIC_DIR")
    max_upload_bytes: int = Field(default=10_485_760, alias="MAX_UPLOAD_BYTES")  # 10 MB


# Module-level singleton
settings = Settings()
