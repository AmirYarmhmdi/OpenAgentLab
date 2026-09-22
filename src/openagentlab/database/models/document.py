"""File guide.

- Use: Defines the SQLAlchemy table model for documents.
- Usage: Import Document from openagentlab.database.models.document.
- Duties: Defines Document and related helper logic.
- Depends on: Project modules: openagentlab.database.base, and
  openagentlab.database.enums.
"""

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
    from openagentlab.database.models.user import User


class Document(TimestampMixin, Base):
    """Logical document within an OpenAgentLab session."""

    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "status in ('uploaded', 'processing', 'indexed', 'failed')",
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
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=DocumentStatus.UPLOADED.value,
        server_default=DocumentStatus.UPLOADED.value,
        nullable=False,
    )
    indexing_error_code: Mapped[str | None] = mapped_column(String(64))
    indexing_error_message: Mapped[str | None] = mapped_column(String(512))

    session: Mapped[ConversationSession] = relationship(back_populates="documents")
    user: Mapped[User | None] = relationship(back_populates="documents")
    file_metadata: Mapped[FileMetadata | None] = relationship(
        back_populates="document",
        uselist=False,
    )
