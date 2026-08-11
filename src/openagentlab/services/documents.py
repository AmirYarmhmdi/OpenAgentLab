"""File guide.

- Use: Coordinates document-facing API operations through upload persistence.
- Usage: Import DocumentService and StoredDocumentService from
  openagentlab.services.documents.
- Duties: Defines stable document records for uploaded files and validation.
- Depends on: Project modules: openagentlab.core.exceptions,
  openagentlab.repositories.file_metadata, and openagentlab.services.upload.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from fastapi import status

from openagentlab.core.exceptions import AppException
from openagentlab.repositories.file_metadata import (
    FileMetadataRecord,
    FileMetadataRepository,
)
from openagentlab.services.upload import UploadInput, UploadService


class DocumentNotFoundError(AppException):
    """Raised when a requested document ID is not known."""

    def __init__(self, document_id: UUID) -> None:
        super().__init__(
            "Document not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="DOCUMENT_NOT_FOUND",
            details={"document_id": str(document_id)},
        )


class InvalidDocumentUploadError(AppException):
    """Raised when an upload request is structurally invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_DOCUMENT_UPLOAD",
        )


@dataclass(frozen=True)
class DocumentUpload:
    filename: str
    content: bytes
    content_type: str | None = None


@dataclass(frozen=True)
class DocumentRecord:
    document_id: UUID
    filename: str
    content_type: str | None
    status: str
    created_at: datetime
    workflow_id: UUID | None = None


class DocumentService(Protocol):
    async def upload_document(self, upload: DocumentUpload) -> DocumentRecord:
        """Store a document upload and return its public document record."""

    async def list_documents(self) -> list[DocumentRecord]:
        """Return documents known to the application."""

    async def ensure_documents_exist(self, document_ids: list[UUID]) -> None:
        """Raise if any document ID is unknown."""


class StoredDocumentService:
    """Expose uploaded file metadata as the current document API abstraction."""

    def __init__(
        self,
        *,
        upload_service: UploadService,
        file_metadata_repository: FileMetadataRepository,
    ) -> None:
        self._upload_service = upload_service
        self._file_metadata_repository = file_metadata_repository

    async def upload_document(self, upload: DocumentUpload) -> DocumentRecord:
        filename = upload.filename.strip()
        if not filename:
            raise InvalidDocumentUploadError("Uploaded document filename is required.")

        record = await self._upload_service.upload(
            UploadInput(
                original_filename=filename,
                content=upload.content,
                content_type=upload.content_type,
            )
        )
        return _document_record_from_file_metadata(record)

    async def list_documents(self) -> list[DocumentRecord]:
        records = await self._file_metadata_repository.list()
        return [_document_record_from_file_metadata(record) for record in records]

    async def ensure_documents_exist(self, document_ids: list[UUID]) -> None:
        seen: set[UUID] = set()
        for document_id in document_ids:
            if document_id in seen:
                continue
            seen.add(document_id)
            record = await self._file_metadata_repository.get_by_id(document_id)
            if record is None:
                raise DocumentNotFoundError(document_id)


def _document_record_from_file_metadata(record: FileMetadataRecord) -> DocumentRecord:
    return DocumentRecord(
        document_id=record.id,
        filename=record.original_filename,
        content_type=record.content_type,
        status=record.status,
        created_at=record.created_at,
    )
