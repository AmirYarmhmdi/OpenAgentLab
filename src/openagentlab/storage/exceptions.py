class StorageError(Exception):
    """Base error for storage provider failures."""


class InvalidStorageKeyError(StorageError):
    """Raised when a logical storage key is unsafe or invalid."""


class StorageObjectNotFoundError(StorageError):
    """Raised when a requested storage object does not exist."""
