"""File guide.

- Use: Contains unit tests for upload persistence behavior.
- Usage: Run this file with pytest when checking related behavior.
- Duties: Builds test data, calls the public API, and checks expected results.
- Depends on: Project modules: openagentlab.database, openagentlab.database.engine,
  openagentlab.database.session, openagentlab.repositories.file_metadata,
  openagentlab.services.upload, and 1 more.
"""

import asyncio
import os

import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import AsyncSession

from openagentlab.database import Base
from openagentlab.database.engine import create_database_engine
from openagentlab.database.session import create_session_factory
from openagentlab.repositories.file_metadata import SQLAlchemyFileMetadataRepository
from openagentlab.services.upload import UploadInput, UploadService
from openagentlab.storage.local import LocalStorageProvider

TEST_DATABASE_URL = os.environ.get("OPENAGENTLAB_TEST_DATABASE_URL")


def test_upload_persists_metadata_and_retrievable_binary_content(tmp_path) -> None:
    if not TEST_DATABASE_URL:
        pytest.skip("OPENAGENTLAB_TEST_DATABASE_URL is required for persistence tests.")
    if not is_safe_test_database_url(TEST_DATABASE_URL):
        pytest.skip(
            "OPENAGENTLAB_TEST_DATABASE_URL must point to a database ending in _test.",
        )

    asyncio.run(_run_upload_persistence_test(tmp_path))


def is_safe_test_database_url(database_url: str | None) -> bool:
    if not database_url:
        return False

    try:
        database_name = make_url(database_url).database
    except ArgumentError:
        return False

    return bool(database_name and database_name.endswith("_test"))


@pytest.mark.parametrize(
    ("database_url", "expected"),
    (
        (
            "postgresql+asyncpg://openagentlab:password@localhost/openagentlab_test",
            True,
        ),
        (
            "postgresql+asyncpg://openagentlab:password@localhost/openagentlab",
            False,
        ),
        (
            "postgresql+asyncpg://openagentlab:password@localhost/production",
            False,
        ),
        ("not a database url", False),
    ),
)
def test_postgres_persistence_guard_requires_test_database_name(
    database_url,
    expected,
) -> None:
    assert is_safe_test_database_url(database_url) is expected


async def _run_upload_persistence_test(tmp_path) -> None:
    engine = create_database_engine(TEST_DATABASE_URL)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

        session_factory = create_session_factory(engine)
        async with session_factory() as session:
            record = await _upload_with_real_repository(session, tmp_path)
            repository = SQLAlchemyFileMetadataRepository(session)
            persisted = await repository.get_by_id(record.id)

        assert persisted is not None
        assert persisted.id == record.id
        assert persisted.storage_key == record.storage_key
        assert not os.path.isabs(persisted.storage_key)
        assert persisted.storage_key.startswith("files/")
        assert (
            LocalStorageProvider(tmp_path).open(persisted.storage_key) == b"a,b\n1,2\n"
        )
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


async def _upload_with_real_repository(
    session: AsyncSession,
    tmp_path,
):
    service = UploadService(
        LocalStorageProvider(tmp_path),
        SQLAlchemyFileMetadataRepository(session),
    )
    return await service.upload(
        UploadInput(
            original_filename="../Report.CSV",
            content=b"a,b\n1,2\n",
            content_type="text/csv",
        ),
    )
