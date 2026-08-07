import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import PurePath

from fastapi import status

from openagentlab.core.exceptions import AppException
from openagentlab.database.enums import FileStorageStatus
from openagentlab.repositories.file_metadata import (
    FileMetadataCreate,
    FileMetadataRecord,
    FileMetadataRepository,
)
from openagentlab.storage.base import StorageProvider

logger = logging.getLogger(__name__)

SUPPORTED_UPLOAD_EXTENSIONS = frozenset(
    {
        ".pdf",
        ".csv",
        ".xlsx",
        ".docx",
        ".txt",
        ".md",
    },
)


class UnsupportedUploadFileTypeError(AppException):
    """Raised when an uploaded file extension is not supported."""

    def __init__(self, filename: str, extension: str | None) -> None:
        details = {
            "filename": filename,
            "extension": extension,
            "supported_extensions": sorted(SUPPORTED_UPLOAD_EXTENSIONS),
        }
        super().__init__(
            "Unsupported upload file type.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="UNSUPPORTED_UPLOAD_FILE_TYPE",
            details=details,
        )


@dataclass(frozen=True)
class UploadInput:
    original_filename: str
    content: bytes
    content_type: str | None = None


class UploadService:
    """Coordinate file upload storage and metadata persistence."""

    def __init__(
        self,
        storage_provider: StorageProvider,
        file_metadata_repository: FileMetadataRepository,
        *,
        file_id_factory: Callable[[], uuid.UUID] = uuid.uuid4,
        storage_backend: str = "local",
    ) -> None:
        self._storage_provider = storage_provider
        self._file_metadata_repository = file_metadata_repository
        self._file_id_factory = file_id_factory
        self._storage_backend = storage_backend

    async def upload(self, upload_input: UploadInput) -> FileMetadataRecord:
        normalized_extension = self._validate_extension(
            upload_input.original_filename,
        )
        file_id = self._file_id_factory()
        storage_key = self._build_storage_key(file_id, normalized_extension)

        stored = False
        try:
            stored_object = self._storage_provider.save(
                storage_key,
                upload_input.content,
            )
            stored = True
            return await self._file_metadata_repository.create(
                FileMetadataCreate(
                    id=file_id,
                    original_filename=upload_input.original_filename,
                    storage_key=stored_object.storage_key,
                    storage_backend=self._storage_backend,
                    content_type=upload_input.content_type,
                    normalized_extension=normalized_extension,
                    size_bytes=stored_object.size_bytes,
                    status=FileStorageStatus.STORED,
                ),
            )
        except Exception:
            if stored:
                self._cleanup_stored_object(storage_key)
            raise

    @staticmethod
    def _validate_extension(filename: str) -> str:
        extension = PurePath(filename).suffix.lower()
        if extension not in SUPPORTED_UPLOAD_EXTENSIONS:
            raise UnsupportedUploadFileTypeError(
                filename=filename,
                extension=extension or None,
            )

        return extension

    @staticmethod
    def _build_storage_key(file_id: uuid.UUID, extension: str) -> str:
        return f"files/{file_id}/content{extension}"

    def _cleanup_stored_object(self, storage_key: str) -> None:
        try:
            self._storage_provider.delete(storage_key)
        except Exception:
            logger.warning(
                "Failed to clean up stored object after metadata persistence "
                "failure: %s",
                storage_key,
                exc_info=True,
            )
