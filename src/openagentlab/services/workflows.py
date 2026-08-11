"""File guide.

- Use: Reads public workflow execution status through repository abstractions.
- Usage: Import WorkflowStatusService from openagentlab.services.workflows.
- Duties: Defines workflow status API service and not-found errors.
- Depends on: Project modules: openagentlab.core.exceptions and
  openagentlab.repositories.workflow_execution.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from fastapi import status

from openagentlab.core.exceptions import AppException
from openagentlab.repositories.workflow_execution import (
    WorkflowExecutionRecord,
    WorkflowExecutionRepository,
)


class WorkflowNotFoundError(AppException):
    """Raised when a workflow execution ID is not known."""

    def __init__(self, workflow_id: UUID) -> None:
        super().__init__(
            "Workflow not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="WORKFLOW_NOT_FOUND",
            details={"workflow_id": str(workflow_id)},
        )


@dataclass(frozen=True)
class WorkflowStatusRecord:
    workflow_id: UUID
    status: str
    result: dict[str, Any] | None
    error: str | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class WorkflowStatusService(Protocol):
    async def get_workflow_status(self, workflow_id: UUID) -> WorkflowStatusRecord:
        """Return public workflow status for a workflow execution."""


class RepositoryWorkflowStatusService:
    """Workflow status service backed by workflow execution persistence."""

    def __init__(self, repository: WorkflowExecutionRepository) -> None:
        self._repository = repository

    async def get_workflow_status(self, workflow_id: UUID) -> WorkflowStatusRecord:
        record = await self._repository.get_by_id(workflow_id)
        if record is None:
            raise WorkflowNotFoundError(workflow_id)

        return _workflow_status_from_record(record)


def _workflow_status_from_record(
    record: WorkflowExecutionRecord,
) -> WorkflowStatusRecord:
    return WorkflowStatusRecord(
        workflow_id=record.id,
        status=record.status,
        result=record.output_payload,
        error=record.error_message,
        created_at=record.created_at,
        updated_at=record.updated_at,
        started_at=record.started_at,
        finished_at=record.finished_at,
    )
