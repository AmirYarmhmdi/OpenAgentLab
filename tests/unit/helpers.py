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
        "openagentlab.api.v1.endpoints.health",
    ):
        sys.modules.pop(module_name, None)

    # Import the main module again and build a fresh FastAPI app.
    main = importlib.import_module("openagentlab.main")
    return main.create_app()
