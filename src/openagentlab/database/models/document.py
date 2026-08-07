from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from openagentlab.database.base import Base, TimestampMixin
from openagentlab.database.enums import DocumentStatus

if TYPE_CHECKING:
    from openagentlab.database.models.conversation_session import ConversationSession
    from openagentlab.database.models.file_metadata import FileMetadata


class Document(TimestampMixin, Base):
    """Logical document within an OpenAgentLab session."""

    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "status in ('pending', 'processing', 'ready', 'failed')",
            name="document_status",
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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=DocumentStatus.PENDING.value,
        server_default=DocumentStatus.PENDING.value,
        nullable=False,
    )

    session: Mapped[ConversationSession] = relationship(back_populates="documents")
    file_metadata: Mapped[FileMetadata | None] = relationship(
        back_populates="document",
        uselist=False,
    )
