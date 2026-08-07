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
