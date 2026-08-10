"""File guide.

- Use: Exports repository interfaces and implementations.
- Usage: Import from openagentlab.repositories.__init__ to use the package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.repositories.file_metadata.
"""

from openagentlab.repositories.file_metadata import (
    FileMetadataCreate,
    FileMetadataRecord,
    FileMetadataRepository,
    SQLAlchemyFileMetadataRepository,
)

__all__ = [
    "FileMetadataCreate",
    "FileMetadataRecord",
    "FileMetadataRepository",
    "SQLAlchemyFileMetadataRepository",
]
