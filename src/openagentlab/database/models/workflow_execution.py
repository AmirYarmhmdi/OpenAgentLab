"""File guide.

- Use: Defines the SQLAlchemy table model for workflow executions.
- Usage: Import WorkflowExecution from
  openagentlab.database.models.workflow_execution.
- Duties: Defines WorkflowExecution and related helper logic.
- Depends on: Project modules: openagentlab.database.base, and
  openagentlab.database.enums.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from openagentlab.database.base import Base, TimestampMixin
from openagentlab.database.enums import WorkflowExecutionStatus

if TYPE_CHECKING:
    from openagentlab.database.models.conversation_session import ConversationSession


class WorkflowExecution(TimestampMixin, Base):
    """High-level workflow execution state for OpenAgentLab."""

    __tablename__ = "workflow_executions"
    __table_args__ = (
        CheckConstraint(
            "status in ('pending', 'running', 'completed', 'failed')",
            name="workflow_execution_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id"),
        index=True,
        nullable=False,
    )
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    workflow_version: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowExecutionStatus.PENDING.value,
        server_default=WorkflowExecutionStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    input_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    output_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)
    trace_id: Mapped[str | None] = mapped_column(String(255))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    session: Mapped[ConversationSession] = relationship(
        back_populates="workflow_executions",
    )
