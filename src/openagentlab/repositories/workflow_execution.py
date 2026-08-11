"""File guide.

- Use: Stores and reads workflow execution state behind a repository boundary.
- Usage: Import WorkflowExecutionRecord and SQLAlchemyWorkflowExecutionRepository
  from openagentlab.repositories.workflow_execution.
- Duties: Defines workflow persistence records and SQLAlchemy-backed state updates.
- Depends on: External packages: sqlalchemy. Project modules:
  openagentlab.database.enums and openagentlab.database.models.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from openagentlab.database.enums import (
    ConversationSessionStatus,
    WorkflowExecutionStatus,
)
from openagentlab.database.models.conversation_session import ConversationSession
from openagentlab.database.models.workflow_execution import WorkflowExecution


@dataclass(frozen=True)
class WorkflowExecutionRecord:
    id: UUID
    session_id: UUID
    workflow_name: str
    workflow_version: str | None
    status: str
    input_payload: dict[str, Any] | None
    output_payload: dict[str, Any] | None
    error_message: str | None
    trace_id: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime


class WorkflowExecutionRepository(Protocol):
    async def create(
        self,
        *,
        workflow_name: str,
        input_payload: dict[str, Any] | None = None,
        workflow_version: str | None = None,
        status: WorkflowExecutionStatus = WorkflowExecutionStatus.PENDING,
    ) -> WorkflowExecutionRecord:
        """Create a workflow execution record."""

    async def complete(
        self,
        workflow_id: UUID,
        *,
        output_payload: dict[str, Any] | None = None,
    ) -> WorkflowExecutionRecord:
        """Mark a workflow as completed."""

    async def fail(
        self,
        workflow_id: UUID,
        *,
        error_message: str,
    ) -> WorkflowExecutionRecord:
        """Mark a workflow as failed with a safe error message."""

    async def get_by_id(self, workflow_id: UUID) -> WorkflowExecutionRecord | None:
        """Return a workflow execution record by ID."""


class SQLAlchemyWorkflowExecutionRepository:
    """SQLAlchemy-backed repository for workflow execution state."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        workflow_name: str,
        input_payload: dict[str, Any] | None = None,
        workflow_version: str | None = None,
        status: WorkflowExecutionStatus = WorkflowExecutionStatus.PENDING,
    ) -> WorkflowExecutionRecord:
        conversation_session = ConversationSession(
            id=uuid4(),
            title=workflow_name,
            status=ConversationSessionStatus.ACTIVE.value,
        )
        record = WorkflowExecution(
            id=uuid4(),
            session=conversation_session,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
            status=status.value,
            input_payload=input_payload,
            started_at=(
                datetime.now(UTC) if status is WorkflowExecutionStatus.RUNNING else None
            ),
        )
        self._session.add(record)

        try:
            await self._session.flush()
            await self._session.refresh(record)
            created_record = _to_record(record)
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

        return created_record

    async def complete(
        self,
        workflow_id: UUID,
        *,
        output_payload: dict[str, Any] | None = None,
    ) -> WorkflowExecutionRecord:
        return await self._set_terminal_status(
            workflow_id,
            status=WorkflowExecutionStatus.COMPLETED,
            output_payload=output_payload,
        )

    async def fail(
        self,
        workflow_id: UUID,
        *,
        error_message: str,
    ) -> WorkflowExecutionRecord:
        return await self._set_terminal_status(
            workflow_id,
            status=WorkflowExecutionStatus.FAILED,
            error_message=error_message,
        )

    async def get_by_id(self, workflow_id: UUID) -> WorkflowExecutionRecord | None:
        record = await self._get_model(workflow_id)
        if record is None:
            return None

        return _to_record(record)

    async def _set_terminal_status(
        self,
        workflow_id: UUID,
        *,
        status: WorkflowExecutionStatus,
        output_payload: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> WorkflowExecutionRecord:
        record = await self._get_model(workflow_id)
        if record is None:
            msg = f"Workflow execution not found: {workflow_id}"
            raise KeyError(msg)

        record.status = status.value
        record.output_payload = output_payload
        record.error_message = error_message
        record.finished_at = datetime.now(UTC)

        try:
            await self._session.flush()
            await self._session.refresh(record)
            updated_record = _to_record(record)
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

        return updated_record

    async def _get_model(self, workflow_id: UUID) -> WorkflowExecution | None:
        result = await self._session.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == workflow_id),
        )
        return result.scalar_one_or_none()


def _to_record(workflow: WorkflowExecution) -> WorkflowExecutionRecord:
    return WorkflowExecutionRecord(
        id=workflow.id,
        session_id=workflow.session_id,
        workflow_name=workflow.workflow_name,
        workflow_version=workflow.workflow_version,
        status=workflow.status,
        input_payload=workflow.input_payload,
        output_payload=workflow.output_payload,
        error_message=workflow.error_message,
        trace_id=workflow.trace_id,
        started_at=workflow.started_at,
        finished_at=workflow.finished_at,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
    )
