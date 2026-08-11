"""File guide.

- Use: Defines public API schemas for document endpoints.
- Usage: Import document response models from openagentlab.schemas.documents.
- Duties: Keeps API document schemas separate from database models.
- Depends on: External packages only: datetime, pydantic, and uuid.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    """Response returned after accepting a document upload."""

    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    filename: str
    content_type: str | None = None
    status: str
    workflow_id: UUID | None = None


class DocumentListItem(BaseModel):
    """Document summary returned from the list documents endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    content_type: str | None = None
    status: str
    created_at: datetime


class DocumentListResponse(BaseModel):
    """Response envelope for known documents."""

    documents: list[DocumentListItem]
