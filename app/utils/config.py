"""
Central settings loaded from environment / .env file.
All other modules import `settings` from here — never read os.environ directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────────
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")

    # Bhashini
    bhashini_user_id: str = Field(default="", alias="BHASHINI_USER_ID")
    bhashini_api_key: str = Field(default="", alias="BHASHINI_API_KEY")

    llm_provider: str = Field(default="groq", alias="LLM_PROVIDER")
    llm_model: str = Field(default="llama3-8b-8192", alias="LLM_MODEL")

    # ── Whisper ──────────────────────────────────────────────────────────
    whisper_model: str = Field(default="base", alias="WHISPER_MODEL")

    # ── Pricing / FAISS ──────────────────────────────────────────────────
    faiss_index_path: str = Field(default="data/faiss.index", alias="FAISS_INDEX_PATH")
    faiss_metadata_path: str = Field(
        default="data/product_metadata.csv", alias="FAISS_METADATA_PATH"
    )

    # ── Embeddings ───────────────────────────────────────────────────────
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )

    # ── App ──────────────────────────────────────────────────────────────
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./craftlens.db", alias="DATABASE_URL"
    )
    static_dir: str = Field(default="static", alias="STATIC_DIR")


# Singleton — imported everywhere as `from app.utils.config import settings`
settings = Settings()
