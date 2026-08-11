"""File guide.

- Use: Contains unit tests for settings behavior.
- Usage: Run this file with pytest when checking related behavior.
- Duties: Builds test data, calls the public API, and checks expected results.
- Depends on: Project modules: openagentlab.core.config.
"""

import pytest
from helpers import clear_settings_env
from pydantic import ValidationError

from openagentlab.core.config import Settings


# This checks that normal DEBUG boolean values are accepted.
@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("true", True),
        ("false", False),
        ("1", True),
        ("0", False),
    ),
)
def test_debug_accepts_standard_boolean_values(monkeypatch, value, expected) -> None:
    clear_settings_env(monkeypatch)

    assert Settings(DEBUG=value).DEBUG is expected


# This checks that invalid DEBUG values fail instead of being hidden.
@pytest.mark.parametrize("value", ("release", "random-value"))
def test_debug_rejects_invalid_values(monkeypatch, value) -> None:
    clear_settings_env(monkeypatch)

    with pytest.raises(ValidationError):
        Settings(DEBUG=value)


# This checks that environment variables can override default settings.
def test_environment_variables_override_defaults(monkeypatch) -> None:
    clear_settings_env(monkeypatch)
    monkeypatch.setenv("APP_NAME", "AuditName")
    monkeypatch.setenv("ENVIRONMENT", "audit")

    settings = Settings()

    assert settings.APP_NAME == "AuditName"
    assert settings.ENVIRONMENT == "audit"


def test_local_storage_root_has_development_default(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    assert Settings().LOCAL_STORAGE_ROOT == "storage"


def test_rag_settings_have_development_defaults(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = Settings()

    assert settings.QDRANT_COLLECTION_NAME == "openagentlab_rag_chunks"
    assert settings.OPENAGENTLAB_PLANNER_MODEL == "gpt-4.1-mini"
    assert settings.OPENAGENTLAB_TOOL_SELECTOR_MODEL == "gpt-4.1-mini"
    assert settings.OPENAGENTLAB_RESPONSE_MODEL == "gpt-4.1-mini"
    assert settings.RAG_EMBEDDING_MODEL == "text-embedding-3-small"
    assert settings.RAG_EMBEDDING_DIMENSION == 1536
    assert settings.RAG_CHUNK_SIZE == 800
    assert settings.RAG_CHUNK_OVERLAP == 100


def test_langfuse_observability_is_disabled_by_default(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = Settings()

    assert settings.LANGFUSE_ENABLED is False
    assert settings.LANGFUSE_PUBLIC_KEY is None
    assert settings.LANGFUSE_SECRET_KEY is None
    assert settings.LANGFUSE_BASE_URL is None
