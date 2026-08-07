from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from openagentlab.database.base import Base, TimestampMixin
from openagentlab.database.enums import ConversationSessionStatus

if TYPE_CHECKING:
    from openagentlab.database.models.document import Document
    from openagentlab.database.models.user import User
    from openagentlab.database.models.workflow_execution import WorkflowExecution


class ConversationSession(TimestampMixin, Base):
    """OpenAgentLab application session, not a SQLAlchemy DB session."""

    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint(
            "status in ('active', 'archived')",
            name="session_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(32),
        default=ConversationSessionStatus.ACTIVE.value,
        server_default=ConversationSessionStatus.ACTIVE.value,
        nullable=False,
    )

    user: Mapped[User | None] = relationship(back_populates="sessions")
    documents: Mapped[list[Document]] = relationship(back_populates="session")
    workflow_executions: Mapped[list[WorkflowExecution]] = relationship(
        back_populates="session",
    )
