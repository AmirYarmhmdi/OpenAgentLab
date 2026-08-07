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
