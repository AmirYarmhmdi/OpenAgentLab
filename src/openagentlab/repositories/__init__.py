"""File guide.

- Use: Exports repository interfaces and implementations.
- Usage: Import from openagentlab.repositories.__init__ to use the package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.repositories.conversations,
  openagentlab.repositories.documents, and openagentlab.repositories.file_metadata.
"""

from openagentlab.repositories.conversations import (
    ConversationDocumentReferenceCreate,
    ConversationDocumentReferenceRecord,
    ConversationMessageCreate,
    ConversationMessageRecord,
    ConversationRepository,
    ConversationSessionRecord,
    SQLAlchemyConversationRepository,
)
from openagentlab.repositories.documents import (
    DocumentRepository,
    SQLAlchemyDocumentRepository,
    UploadedDocumentCreate,
    UploadedDocumentRecord,
)
from openagentlab.repositories.file_metadata import (
    FileMetadataCreate,
    FileMetadataRecord,
    FileMetadataRepository,
    SQLAlchemyFileMetadataRepository,
)
from openagentlab.repositories.users import (
    SQLAlchemyUserRepository,
    UserRecord,
    UserRepository,
)

__all__ = [
    "ConversationDocumentReferenceCreate",
    "ConversationDocumentReferenceRecord",
    "ConversationMessageCreate",
    "ConversationMessageRecord",
    "ConversationRepository",
    "ConversationSessionRecord",
    "DocumentRepository",
    "FileMetadataCreate",
    "FileMetadataRecord",
    "FileMetadataRepository",
    "SQLAlchemyDocumentRepository",
    "SQLAlchemyFileMetadataRepository",
    "SQLAlchemyConversationRepository",
    "SQLAlchemyUserRepository",
    "UserRecord",
    "UserRepository",
    "UploadedDocumentCreate",
    "UploadedDocumentRecord",
]
