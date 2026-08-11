"""File guide.

- Use: Contains unit tests for helpers behavior.
- Usage: Run this file with pytest when checking related behavior.
- Duties: Builds test data, calls the public API, and checks expected results.
- Depends on: External packages only: importlib, and sys.
"""

import importlib
import sys

# These are the settings variables that can affect the Phase 3 app.
SETTINGS_ENV_VARS = (
    "APP_NAME",
    "APP_VERSION",
    "ENVIRONMENT",
    "DEBUG",
    "API_V1_PREFIX",
    "LOG_LEVEL",
    "HOST",
    "PORT",
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "QDRANT_COLLECTION_NAME",
    "OPENAGENTLAB_PLANNER_MODEL",
    "OPENAGENTLAB_TOOL_SELECTOR_MODEL",
    "OPENAGENTLAB_RESPONSE_MODEL",
    "RAG_EMBEDDING_MODEL",
    "RAG_EMBEDDING_DIMENSION",
    "RAG_CHUNK_SIZE",
    "RAG_CHUNK_OVERLAP",
    "EVALUATION_MODEL",
    "EVALUATION_EMBEDDING_MODEL",
    "EVALUATION_ANSWER_RELEVANCY_THRESHOLD",
    "EVALUATION_FAITHFULNESS_THRESHOLD",
    "EVALUATION_CONTEXT_PRECISION_THRESHOLD",
    "EVALUATION_CONTEXT_RECALL_THRESHOLD",
    "EVALUATION_HALLUCINATION_THRESHOLD",
    "LANGFUSE_HOST",
    "LANGFUSE_ENABLED",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_BASE_URL",
    "LOCAL_STORAGE_ROOT",
)


# This removes app settings from the test environment and clears the settings cache.
def clear_settings_env(monkeypatch) -> None:
    for env_var in SETTINGS_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)

    from openagentlab.core.config import get_settings

    get_settings.cache_clear()


# This creates a fresh app that is not affected by the developer shell.
def create_isolated_app(monkeypatch):
    clear_settings_env(monkeypatch)

    # Remove imported app modules so they reload with clean settings.
    for module_name in (
        "openagentlab.main",
        "openagentlab.api.router",
        "openagentlab.api.v1.router",
        "openagentlab.api.v1.endpoints.documents",
        "openagentlab.api.v1.endpoints.health",
        "openagentlab.api.v1.endpoints.questions",
        "openagentlab.api.v1.endpoints.workflows",
        "openagentlab.api.dependencies",
    ):
        sys.modules.pop(module_name, None)

    # Import the main module again and build a fresh FastAPI app.
    main = importlib.import_module("openagentlab.main")
    return main.create_app()
