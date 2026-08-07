from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from openagentlab.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from openagentlab.database.models.conversation_session import ConversationSession


class User(TimestampMixin, Base):
    """Foundation user record for future authentication support."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str | None] = mapped_column(String(320), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    sessions: Mapped[list[ConversationSession]] = relationship(
        back_populates="user",
    )
