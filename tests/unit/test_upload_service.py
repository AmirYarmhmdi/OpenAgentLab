import asyncio
from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from openagentlab.database.enums import FileStorageStatus
from openagentlab.repositories.file_metadata import (
    FileMetadataCreate,
    FileMetadataRecord,
)
from openagentlab.services.upload import (
    UnsupportedUploadFileTypeError,
    UploadInput,
    UploadService,
)
from openagentlab.storage.base import StoredObject
from openagentlab.storage.exceptions import StorageError


class FakeStorageProvider:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.deleted_keys: list[str] = []
        self.fail_save = False
        self.fail_delete = False

    def save(self, storage_key: str, content: bytes) -> StoredObject:
        if self.fail_save:
            msg = "storage failed"
            raise StorageError(msg)
        self.objects[storage_key] = content
        return StoredObject(storage_key=storage_key, size_bytes=len(content))

    def open(self, storage_key: str) -> bytes:
        return self.objects[storage_key]

    def delete(self, storage_key: str) -> None:
        if self.fail_delete:
            msg = "cleanup failed"
            raise StorageError(msg)
        self.deleted_keys.append(storage_key)
        self.objects.pop(storage_key, None)

    def exists(self, storage_key: str) -> bool:
        return storage_key in self.objects


class FakeFileMetadataRepository:
    def __init__(self) -> None:
        self.records: dict[UUID, FileMetadataRecord] = {}
        self.created: list[FileMetadataCreate] = []
        self.fail_create = False

    async def create(self, metadata: FileMetadataCreate) -> FileMetadataRecord:
        if self.fail_create:
            msg = "metadata failed"
            raise RuntimeError(msg)
        now = datetime.now(UTC)
        record = FileMetadataRecord(
            id=metadata.id,
            document_id=metadata.document_id,
            original_filename=metadata.original_filename,
            storage_key=metadata.storage_key,
            storage_backend=metadata.storage_backend,
            content_type=metadata.content_type,
            normalized_extension=metadata.normalized_extension,
            size_bytes=metadata.size_bytes,
            status=metadata.status.value,
            checksum_sha256=metadata.checksum_sha256,
            created_at=now,
            updated_at=now,
        )
        self.created.append(metadata)
        self.records[record.id] = record
        return record

    async def get_by_id(self, file_id: UUID) -> FileMetadataRecord | None:
        return self.records.get(file_id)


def run_upload(service: UploadService, upload_input: UploadInput) -> FileMetadataRecord:
    return asyncio.run(service.upload(upload_input))


def test_upload_service_stores_supported_upload_and_metadata() -> None:
    storage = FakeStorageProvider()
    repository = FakeFileMetadataRepository()
    file_id = UUID("11111111-1111-4111-8111-111111111111")
    service = UploadService(storage, repository, file_id_factory=lambda: file_id)

    record = run_upload(
        service,
        UploadInput("Report.PDF", b"pdf bytes", "application/pdf"),
    )

    assert record.id == file_id
    assert record.original_filename == "Report.PDF"
    assert record.storage_key == f"files/{file_id}/content.pdf"
    assert record.storage_backend == "local"
    assert record.content_type == "application/pdf"
    assert record.normalized_extension == ".pdf"
    assert record.size_bytes == len(b"pdf bytes")
    assert record.status == FileStorageStatus.STORED.value
    assert storage.open(record.storage_key) == b"pdf bytes"


def test_upload_service_duplicate_filenames_get_unique_ids_and_storage_keys() -> None:
    storage = FakeStorageProvider()
    repository = FakeFileMetadataRepository()
    ids = iter(
        [
            UUID("11111111-1111-4111-8111-111111111111"),
            UUID("22222222-2222-4222-8222-222222222222"),
        ]
    )
    service = UploadService(storage, repository, file_id_factory=lambda: next(ids))

    first = run_upload(service, UploadInput("same.csv", b"first"))
    second = run_upload(service, UploadInput("same.csv", b"second"))

    assert first.id != second.id
    assert first.storage_key != second.storage_key
    assert storage.open(first.storage_key) == b"first"
    assert storage.open(second.storage_key) == b"second"


def test_upload_service_rejects_unsupported_extension() -> None:
    service = UploadService(FakeStorageProvider(), FakeFileMetadataRepository())

    with pytest.raises(UnsupportedUploadFileTypeError) as exc_info:
        run_upload(service, UploadInput("malware.exe", b"nope"))

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == "UNSUPPORTED_UPLOAD_FILE_TYPE"


def test_upload_service_propagates_storage_provider_failure() -> None:
    storage = FakeStorageProvider()
    storage.fail_save = True
    repository = FakeFileMetadataRepository()
    service = UploadService(storage, repository)

    with pytest.raises(StorageError):
        run_upload(service, UploadInput("report.pdf", b"data"))

    assert repository.created == []
    assert storage.deleted_keys == []


def test_upload_service_cleans_up_stored_object_when_metadata_fails_before_commit() -> (
    None
):
    storage = FakeStorageProvider()
    repository = FakeFileMetadataRepository()
    repository.fail_create = True
    file_id = UUID("11111111-1111-4111-8111-111111111111")
    service = UploadService(storage, repository, file_id_factory=lambda: file_id)

    with pytest.raises(RuntimeError, match="metadata failed"):
        run_upload(service, UploadInput("report.md", b"# report"))

    storage_key = f"files/{file_id}/content.md"
    assert storage.deleted_keys == [storage_key]
    assert storage.exists(storage_key) is False


def test_upload_service_reraises_metadata_error_when_cleanup_delete_fails() -> None:
    storage = FakeStorageProvider()
    storage.fail_delete = True
    repository = FakeFileMetadataRepository()
    repository.fail_create = True
    file_id = UUID("11111111-1111-4111-8111-111111111111")
    service = UploadService(storage, repository, file_id_factory=lambda: file_id)

    with pytest.raises(RuntimeError, match="metadata failed"):
        run_upload(service, UploadInput("report.md", b"# report"))

    assert storage.exists(f"files/{file_id}/content.md") is True


def test_upload_service_accepts_zero_byte_upload() -> None:
    service = UploadService(FakeStorageProvider(), FakeFileMetadataRepository())

    record = run_upload(service, UploadInput("empty.txt", b""))

    assert record.size_bytes == 0


def test_fake_repository_get_by_id_returns_created_metadata() -> None:
    repository = FakeFileMetadataRepository()
    metadata = FileMetadataCreate(
        id=uuid4(),
        original_filename="notes.txt",
        storage_key="files/x/content.txt",
        storage_backend="local",
        content_type="text/plain",
        normalized_extension=".txt",
        size_bytes=5,
    )

    record = asyncio.run(repository.create(metadata))

    assert asyncio.run(repository.get_by_id(record.id)) == replace(record)
