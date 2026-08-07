import asyncio

import pytest
from helpers import clear_settings_env
from sqlalchemy.ext.asyncio import AsyncSession

from openagentlab.core.config import Settings
from openagentlab.database import Base, models
from openagentlab.database.engine import create_database_engine, get_database_url
from openagentlab.database.session import create_session_factory


def test_all_initial_models_are_registered_with_metadata() -> None:
    assert models.User.__tablename__ == "users"
    assert sorted(Base.metadata.tables) == [
        "documents",
        "file_metadata",
        "sessions",
        "users",
        "workflow_executions",
    ]


def test_metadata_uses_deterministic_naming_convention() -> None:
    assert Base.metadata.naming_convention == {
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


def test_constraints_and_indexes_match_initial_schema() -> None:
    sessions = Base.metadata.tables["sessions"]
    documents = Base.metadata.tables["documents"]
    file_metadata = Base.metadata.tables["file_metadata"]
    workflow_executions = Base.metadata.tables["workflow_executions"]

    assert {constraint.name for constraint in sessions.constraints} >= {
        "ck_sessions_session_status",
        "fk_sessions_user_id_users",
        "pk_sessions",
    }
    assert {index.name for index in documents.indexes} == {
        "ix_documents_session_id",
    }
    assert file_metadata.c.document_id.unique is True
    assert {constraint.name for constraint in file_metadata.constraints} >= {
        "ck_file_metadata_file_metadata_size_bytes_non_negative",
        "uq_file_metadata_document_id",
    }
    assert {index.name for index in workflow_executions.indexes} == {
        "ix_workflow_executions_session_id",
        "ix_workflow_executions_status",
    }


def test_database_url_is_loaded_from_settings(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://openagentlab:password@postgres/openagentlab"
    )

    assert get_database_url(settings) == (
        "postgresql+asyncpg://openagentlab:password@postgres/openagentlab"
    )


def test_database_url_is_required_before_connecting(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = Settings(DATABASE_URL=None)

    with pytest.raises(RuntimeError, match="DATABASE_URL must be set"):
        get_database_url(settings)


def test_async_engine_and_session_factory_use_asyncpg_url() -> None:
    engine = create_database_engine(
        "postgresql+asyncpg://openagentlab:password@localhost/openagentlab"
    )
    session_factory = create_session_factory(engine)

    assert engine.url.drivername == "postgresql+asyncpg"
    assert session_factory.class_ is AsyncSession
    assert session_factory.kw["expire_on_commit"] is False

    asyncio.run(engine.dispose())
