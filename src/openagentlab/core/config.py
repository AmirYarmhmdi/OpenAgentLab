from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# This class defines all settings the backend needs for Phase 3.
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
