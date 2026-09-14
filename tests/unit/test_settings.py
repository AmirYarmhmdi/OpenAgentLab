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


def build_test_settings(**values: object) -> Settings:
    return Settings(_env_file=None, **values)


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

    assert build_test_settings(DEBUG=value).DEBUG is expected


# This checks that invalid DEBUG values fail instead of being hidden.
@pytest.mark.parametrize("value", ("release", "random-value"))
def test_debug_rejects_invalid_values(monkeypatch, value) -> None:
    clear_settings_env(monkeypatch)

    with pytest.raises(ValidationError):
        build_test_settings(DEBUG=value)


# This checks that environment variables can override default settings.
def test_environment_variables_override_defaults(monkeypatch) -> None:
    clear_settings_env(monkeypatch)
    monkeypatch.setenv("APP_NAME", "AuditName")
    monkeypatch.setenv("ENVIRONMENT", "audit")

    settings = build_test_settings()

    assert settings.APP_NAME == "AuditName"
    assert settings.ENVIRONMENT == "audit"


def test_local_storage_root_has_development_default(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = build_test_settings()

    assert settings.STORAGE_BACKEND == "local"
    assert settings.LOCAL_STORAGE_ROOT == "storage"
    assert settings.AZURE_STORAGE_ACCOUNT_NAME is None
    assert settings.AZURE_STORAGE_CONTAINER_NAME is None
    assert settings.AZURE_STORAGE_MANAGED_IDENTITY_CLIENT_ID is None


def test_runtime_configuration_overrides_storage_backend_and_secrets(
    monkeypatch,
) -> None:
    clear_settings_env(monkeypatch)
    monkeypatch.setenv("STORAGE_BACKEND", "azure_blob")
    monkeypatch.setenv("OPENAI_API_KEY", "runtime-openai-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://runtime-db")
    monkeypatch.setenv("QDRANT_API_KEY", "runtime-qdrant-key")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "runtime-langfuse-secret")
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "openagentlabstorage")
    monkeypatch.setenv("AZURE_STORAGE_CONTAINER_NAME", "openagentlab-files")
    monkeypatch.setenv(
        "AZURE_STORAGE_MANAGED_IDENTITY_CLIENT_ID",
        "11111111-1111-4111-8111-111111111111",
    )

    settings = build_test_settings()

    assert settings.STORAGE_BACKEND == "azure_blob"
    assert settings.OPENAI_API_KEY == "runtime-openai-key"
    assert settings.DATABASE_URL == "postgresql+asyncpg://runtime-db"
    assert settings.QDRANT_API_KEY == "runtime-qdrant-key"
    assert settings.LANGFUSE_SECRET_KEY == "runtime-langfuse-secret"
    assert settings.AZURE_STORAGE_ACCOUNT_NAME == "openagentlabstorage"
    assert settings.AZURE_STORAGE_CONTAINER_NAME == "openagentlab-files"
    assert (
        settings.AZURE_STORAGE_MANAGED_IDENTITY_CLIENT_ID
        == "11111111-1111-4111-8111-111111111111"
    )


def test_rag_settings_have_development_defaults(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = build_test_settings()

    assert settings.QDRANT_COLLECTION_NAME == "openagentlab_rag_chunks"
    assert settings.OPENAI_PLANNER_MODEL == "gpt-4o-mini"
    assert settings.OPENAI_RESPONSE_MODEL == "gpt-4o-mini"
    assert settings.OPENAI_EMBEDDING_MODEL == "text-embedding-3-small"
    assert settings.OPENAGENTLAB_TOOL_SELECTOR_MODEL == "gpt-4.1-mini"
    assert settings.RAG_EMBEDDING_DIMENSION == 1536
    assert settings.RAG_CHUNK_SIZE == 800
    assert settings.RAG_CHUNK_OVERLAP == 100


def test_openai_model_settings_can_be_overridden(monkeypatch) -> None:
    clear_settings_env(monkeypatch)
    monkeypatch.setenv("OPENAI_PLANNER_MODEL", "planner-test-model")
    monkeypatch.setenv("OPENAI_RESPONSE_MODEL", "response-test-model")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "embedding-test-model")

    settings = build_test_settings()

    assert settings.OPENAI_PLANNER_MODEL == "planner-test-model"
    assert settings.OPENAI_RESPONSE_MODEL == "response-test-model"
    assert settings.OPENAI_EMBEDDING_MODEL == "embedding-test-model"


def test_evaluation_settings_have_baseline_defaults(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = build_test_settings()

    assert settings.EVALUATION_MODEL == "gpt-4.1-mini"
    assert settings.EVALUATION_EMBEDDING_MODEL == "text-embedding-3-small"
    assert settings.EVALUATION_ANSWER_RELEVANCY_THRESHOLD == 0.70
    assert settings.EVALUATION_FAITHFULNESS_THRESHOLD == 0.70
    assert settings.EVALUATION_CONTEXT_PRECISION_THRESHOLD == 0.70
    assert settings.EVALUATION_CONTEXT_RECALL_THRESHOLD == 0.70
    assert settings.EVALUATION_HALLUCINATION_THRESHOLD == 0.30


def test_langfuse_observability_is_disabled_by_default(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = build_test_settings()

    assert settings.LANGFUSE_ENABLED is False
    assert settings.LANGFUSE_PUBLIC_KEY is None
    assert settings.LANGFUSE_SECRET_KEY is None
    assert settings.LANGFUSE_BASE_URL is None
