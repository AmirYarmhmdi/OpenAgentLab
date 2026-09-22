"""File guide.

- Use: Provides conversation session APIs and bounded history building.
- Usage: Import ConversationService and ConversationHistoryBuilder.
- Duties: Validates sessions and exposes PostgreSQL-backed chat state.
- Depends on: Project modules: core exceptions and conversation repositories.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from fastapi import status

from openagentlab.core.exceptions import AppException
from openagentlab.repositories.conversations import (
    ConversationMessageRecord,
    ConversationRepository,
    ConversationSessionRecord,
)


class ConversationSessionNotFoundError(AppException):
    """Raised when a requested reusable conversation session is unknown."""

    def __init__(self, session_id: UUID) -> None:
        super().__init__(
            "Conversation session not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="CONVERSATION_SESSION_NOT_FOUND",
            details={"session_id": str(session_id)},
        )


@dataclass(frozen=True)
class ConversationHistoryItem:
    role: str
    content: str


@dataclass(frozen=True)
class ConversationSessionSummary:
    id: UUID
    title: str | None
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ConversationMessageView:
    id: UUID
    role: str
    sequence: int
    content: str
    workflow_id: UUID | None
    status: str
    error_message: str | None
    citations: tuple[dict, ...]
    sources: tuple[dict, ...]
    document_references: tuple[dict, ...]
    created_at: datetime


@dataclass(frozen=True)
class ConversationSessionView:
    id: UUID
    title: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    messages: tuple[ConversationMessageView, ...]


class ConversationService(Protocol):
    async def list_sessions(
        self, *, limit: int = 50
    ) -> list[ConversationSessionSummary]:
        """List recent reusable conversation sessions."""

    async def get_session(self, session_id: UUID) -> ConversationSessionView:
        """Return one reusable session with ordered messages."""


class RepositoryConversationService:
    """Read-only conversation service over the repository boundary."""

    def __init__(self, repository: ConversationRepository, *, user_id: UUID) -> None:
        self._repository = repository
        self._user_id = user_id

    async def list_sessions(
        self,
        *,
        limit: int = 50,
    ) -> list[ConversationSessionSummary]:
        records = await self._repository.list_sessions(
            user_id=self._user_id,
            limit=limit,
        )
        return [_session_summary(record) for record in records]

    async def get_session(self, session_id: UUID) -> ConversationSessionView:
        record = await self._repository.get_session_with_messages(
            session_id,
            user_id=self._user_id,
        )
        if record is None:
            raise ConversationSessionNotFoundError(session_id)
        return _session_view(record)


class ConversationHistoryBuilder:
    """Build bounded recent history for the next answer request."""

    def __init__(
        self,
        repository: ConversationRepository,
        *,
        user_id: UUID,
        max_turns: int,
        max_chars: int,
    ) -> None:
        self._repository = repository
        self._user_id = user_id
        self._max_turns = max_turns
        self._max_chars = max_chars

    async def build(self, session_id: UUID) -> tuple[ConversationHistoryItem, ...]:
        if self._max_turns <= 0:
            return ()

        messages = await self._repository.recent_messages(
            session_id,
            user_id=self._user_id,
            limit=self._max_turns * 2,
        )
        history = [
            ConversationHistoryItem(role=message.role, content=message.content)
            for message in messages
            if message.content.strip()
        ]
        return _trim_history(history, max_chars=self._max_chars)


def _trim_history(
    history: list[ConversationHistoryItem],
    *,
    max_chars: int,
) -> tuple[ConversationHistoryItem, ...]:
    selected: list[ConversationHistoryItem] = []
    used_chars = 0
    for item in reversed(history):
        item_chars = len(item.role) + len(item.content) + 2
        if selected and used_chars + item_chars > max_chars:
            break
        if not selected and item_chars > max_chars:
            selected.append(
                ConversationHistoryItem(
                    role=item.role,
                    content=item.content[:max_chars],
                )
            )
            break
        selected.append(item)
        used_chars += item_chars
    return tuple(reversed(selected))


def _session_summary(record: ConversationSessionRecord) -> ConversationSessionSummary:
    return ConversationSessionSummary(
        id=record.id,
        title=record.title,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _session_view(record: ConversationSessionRecord) -> ConversationSessionView:
    return ConversationSessionView(
        id=record.id,
        title=record.title,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        messages=tuple(_message_view(message) for message in record.messages),
    )


def _message_view(message: ConversationMessageRecord) -> ConversationMessageView:
    return ConversationMessageView(
        id=message.id,
        role=message.role,
        sequence=message.sequence,
        content=message.content,
        workflow_id=message.workflow_id,
        status=message.status,
        error_message=message.error_message,
        citations=message.citations,
        sources=message.sources,
        document_references=tuple(
            {
                "document_id": str(reference.document_id),
                "file_metadata_id": (
                    str(reference.file_metadata_id)
                    if reference.file_metadata_id is not None
                    else None
                ),
                "reference_type": reference.reference_type,
            }
            for reference in message.document_references
        ),
        created_at=message.created_at,
    )
