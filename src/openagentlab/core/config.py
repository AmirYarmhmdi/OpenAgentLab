"""File guide.

- Use: Loads application settings from environment variables and .env files.
- Usage: Import Settings, and get_settings from openagentlab.core.config.
- Duties: Defines Settings, and get_settings and related helper logic.
- Depends on: External packages only: functools, pydantic, and pydantic_settings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# This class defines all settings the backend needs.
class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    # These defaults let the app run locally without a .env file.
    APP_NAME: str = "OpenAgentLab"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str | None = None
    OPENAI_API_KEY: str | None = None
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str = "openagentlab_rag_chunks"
    OPENAGENTLAB_PLANNER_MODEL: str = "gpt-4.1-mini"
    OPENAGENTLAB_TOOL_SELECTOR_MODEL: str = "gpt-4.1-mini"
    OPENAGENTLAB_RESPONSE_MODEL: str = "gpt-4.1-mini"
    RAG_EMBEDDING_MODEL: str = "text-embedding-3-small"
    RAG_EMBEDDING_DIMENSION: int = Field(default=1536, ge=1)
    RAG_CHUNK_SIZE: int = Field(default=800, ge=1)
    RAG_CHUNK_OVERLAP: int = Field(default=100, ge=0)
    EVALUATION_MODEL: str = "gpt-4.1-mini"
    EVALUATION_EMBEDDING_MODEL: str = "text-embedding-3-small"
    EVALUATION_ANSWER_RELEVANCY_THRESHOLD: float = Field(default=0.70, ge=0.0, le=1.0)
    EVALUATION_FAITHFULNESS_THRESHOLD: float = Field(default=0.70, ge=0.0, le=1.0)
    EVALUATION_CONTEXT_PRECISION_THRESHOLD: float = Field(default=0.70, ge=0.0, le=1.0)
    EVALUATION_CONTEXT_RECALL_THRESHOLD: float = Field(default=0.70, ge=0.0, le=1.0)
    EVALUATION_HALLUCINATION_THRESHOLD: float = Field(default=0.30, ge=0.0, le=1.0)
    LANGFUSE_HOST: str | None = None
    LANGFUSE_ENABLED: bool = False
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_BASE_URL: str | None = None
    LOCAL_STORAGE_ROOT: str = "storage"

    # This tells pydantic-settings to also read values from a local .env file.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# This caches settings so the app does not rebuild them on every request.
@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
