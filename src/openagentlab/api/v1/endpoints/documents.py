"""File guide.

- Use: Serves document upload and listing API endpoints.
- Usage: Included by openagentlab.api.v1.router.
- Duties: Validates API requests, delegates to document services, and returns
  stable response schemas.
- Depends on: External packages: fastapi. Project modules:
  openagentlab.api.dependencies, openagentlab.schemas, and
  openagentlab.services.documents.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from openagentlab.api.dependencies import get_document_service
from openagentlab.schemas.documents import (
    DocumentListItem,
    DocumentListResponse,
    DocumentUploadResponse,
)
from openagentlab.services.documents import (
    DocumentService,
    DocumentUpload,
    InvalidDocumentUploadError,
)

router = APIRouter(prefix="/documents")


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document",
)
async def upload_document(
    file: Annotated[UploadFile, File(description="Document file to upload.")],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentUploadResponse:
    if not file.filename:
        raise InvalidDocumentUploadError("Uploaded document filename is required.")

    document = await document_service.upload_document(
        DocumentUpload(
            filename=file.filename,
            content=await file.read(),
            content_type=file.content_type,
        )
    )
    return DocumentUploadResponse(
        document_id=document.document_id,
        filename=document.filename,
        content_type=document.content_type,
        status=document.status,
        workflow_id=document.workflow_id,
    )


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List documents",
)
async def list_documents(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentListResponse:
    documents = await document_service.list_documents()
    return DocumentListResponse(
        documents=[
            DocumentListItem(
                id=document.document_id,
                filename=document.filename,
                content_type=document.content_type,
                status=document.status,
                created_at=document.created_at,
            )
            for document in documents
        ]
    )
