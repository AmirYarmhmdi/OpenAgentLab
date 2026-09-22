"""File guide.

- Use: Contains unit tests for upload persistence behavior.
- Usage: Run this file with pytest when checking related behavior.
- Duties: Builds test data, calls the public API, and checks expected results.
- Depends on: Project modules: openagentlab.database, openagentlab.database.engine,
  openagentlab.database.session, openagentlab.repositories.documents,
  openagentlab.services.upload, and 1 more.
"""

import asyncio
import hashlib
import os
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import AsyncSession

from openagentlab.database import Base
from openagentlab.database.engine import create_database_engine
from openagentlab.database.enums import DocumentStatus, FileStorageStatus
from openagentlab.database.models.document import Document
from openagentlab.database.models.file_metadata import FileMetadata
from openagentlab.database.models.user import User
from openagentlab.database.session import create_session_factory
from openagentlab.repositories.documents import SQLAlchemyDocumentRepository
from openagentlab.services.upload import UploadInput, UploadService
from openagentlab.storage.local import LocalStorageProvider

TEST_DATABASE_URL = os.environ.get("OPENAGENTLAB_TEST_DATABASE_URL")
USER_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")


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
            session.add(
                User(
                    id=USER_ID,
                    issuer="test",
                    external_subject="upload-persistence",
                    email="upload-persistence@example.test",
                )
            )
            await session.commit()
            record = await _upload_with_real_repository(session, tmp_path)
            repository = SQLAlchemyDocumentRepository(session)
            persisted = await repository.get_by_id(
                record.document_id,
                user_id=USER_ID,
            )
            document_row = await session.scalar(
                select(Document).where(Document.id == record.document_id)
            )
            file_metadata_row = await session.scalar(
                select(FileMetadata).where(FileMetadata.id == record.file_metadata_id)
            )

        assert persisted is not None
        assert persisted.document_id == record.document_id
        assert persisted.storage_key == record.storage_key
        assert persisted.status == DocumentStatus.UPLOADED.value
        assert persisted.file_storage_status == FileStorageStatus.STORED.value
        assert persisted.normalized_extension == ".csv"
        assert persisted.size_bytes == len(b"a,b\n1,2\n")
        assert persisted.checksum_sha256 == hashlib.sha256(b"a,b\n1,2\n").hexdigest()
        assert not os.path.isabs(persisted.storage_key)
        assert persisted.user_id == USER_ID
        assert persisted.storage_key.startswith(f"users/{USER_ID}/documents/")
        assert (
            LocalStorageProvider(tmp_path).open(persisted.storage_key) == b"a,b\n1,2\n"
        )
        assert document_row is not None
        assert document_row.user_id == USER_ID
        assert document_row.status == DocumentStatus.UPLOADED.value
        assert file_metadata_row is not None
        assert file_metadata_row.user_id == USER_ID
        assert file_metadata_row.document_id == record.document_id
        assert file_metadata_row.checksum_sha256 == persisted.checksum_sha256
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
        SQLAlchemyDocumentRepository(session),
        user_id=USER_ID,
    )
    return await service.upload(
        UploadInput(
            original_filename="../Report.CSV",
            content=b"a,b\n1,2\n",
            content_type="text/csv",
        ),
    )
