"""File guide.

- Use: Defines database status values shared by SQLAlchemy models.
- Usage: Import ConversationSessionStatus, DocumentStatus, FileStorageStatus, and 1
  more from openagentlab.database.enums.
- Duties: Defines ConversationSessionStatus, DocumentStatus, FileStorageStatus, and
  WorkflowExecutionStatus and related helper logic.
- Depends on: External packages only: enum.
"""

from enum import StrEnum


class ConversationSessionStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class FileStorageStatus(StrEnum):
    STORED = "stored"
    FAILED = "failed"


class WorkflowExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
