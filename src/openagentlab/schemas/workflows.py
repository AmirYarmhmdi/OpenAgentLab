"""File guide.

- Use: Defines public API schemas for workflow status endpoints.
- Usage: Import WorkflowStatusResponse from openagentlab.schemas.workflows.
- Duties: Keeps API workflow schemas separate from database models.
- Depends on: External packages only: datetime, typing, pydantic, and uuid.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkflowStatusResponse(BaseModel):
    """Public workflow execution status."""

    model_config = ConfigDict(from_attributes=True)

    workflow_id: UUID
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
