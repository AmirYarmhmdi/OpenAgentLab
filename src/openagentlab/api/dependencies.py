"""File guide.

- Use: Provides FastAPI dependency factories for API services.
- Usage: Import dependency callables from openagentlab.api.dependencies in routes.
- Duties: Wires repositories, storage, RAG, and service facades without putting
  construction logic in endpoint modules.
- Depends on: External packages: fastapi and sqlalchemy. Project modules:
  openagentlab.core, database, rag, repositories, services, and storage.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from openagentlab.agent.graph import create_agent_graph
from openagentlab.agent.response_generator import OpenAIResponseGenerator
from openagentlab.core.config import (
    ConfigurationError,
    ConfigurationIssue,
    Settings,
    get_settings,
)
from openagentlab.core.exceptions import AppException
from openagentlab.database.session import get_async_session
from openagentlab.rag.chunking.recursive import RecursiveTextChunker
from openagentlab.rag.context.builder import ContextBuilder
from openagentlab.rag.embeddings.openai import OpenAIEmbeddingProvider
from openagentlab.rag.exceptions import VectorStoreError
from openagentlab.rag.indexing import DocumentIndexer
from openagentlab.rag.loaders.base import DocumentLoader
from openagentlab.rag.retrieval.retriever import Retriever
from openagentlab.rag.vectorstores.qdrant import QdrantVectorStore
from openagentlab.repositories.conversations import (
    ConversationRepository,
    SQLAlchemyConversationRepository,
)
from openagentlab.repositories.documents import (
    DocumentRepository,
    SQLAlchemyDocumentRepository,
)
from openagentlab.repositories.file_metadata import (
    FileMetadataRepository,
    SQLAlchemyFileMetadataRepository,
)
from openagentlab.repositories.users import SQLAlchemyUserRepository, UserRepository
from openagentlab.repositories.workflow_execution import (
    SQLAlchemyWorkflowExecutionRepository,
    WorkflowExecutionRepository,
)
from openagentlab.security.auth import (
    AuthenticatedPrincipal,
    ExternalIdentity,
    validate_bearer_token,
)
from openagentlab.services.conversations import (
    ConversationHistoryBuilder,
    ConversationService,
    RepositoryConversationService,
)
from openagentlab.services.document_ingestion import (
    DocumentIngestionService,
    SynchronousDocumentIngestionService,
)
from openagentlab.services.documents import DocumentService, StoredDocumentService
from openagentlab.services.messages import MessageSubmissionService
from openagentlab.services.orchestration import (
    AgentGraphInvoker,
    RoutedQuestionAnsweringService,
)
from openagentlab.services.questions import (
    QuestionAnsweringService,
    QuestionAnsweringUnavailableError,
    RAGQuestionAnsweringService,
)
from openagentlab.services.upload import UploadService
from openagentlab.services.workflows import (
    RepositoryWorkflowStatusService,
    WorkflowStatusService,
)
from openagentlab.skills.document_processing import DocumentProcessingSkill
from openagentlab.storage.azure_blob import AzureBlobStorageProvider
from openagentlab.storage.base import StorageProvider
from openagentlab.storage.local import LocalStorageProvider
from openagentlab.tools.registry import get_runtime_skill_registry, register_skill


def get_storage_provider(
    settings: Annotated[Settings, Depends(get_settings)],
) -> StorageProvider:
    if settings.STORAGE_BACKEND == "local":
        return _get_local_storage_provider(settings.LOCAL_STORAGE_ROOT)

    if settings.STORAGE_BACKEND == "azure_blob":
        account_name = _require_azure_storage_config(
            settings.AZURE_STORAGE_ACCOUNT_NAME,
            "AZURE_STORAGE_ACCOUNT_NAME",
        )
        container_name = _require_azure_storage_config(
            settings.AZURE_STORAGE_CONTAINER_NAME,
            "AZURE_STORAGE_CONTAINER_NAME",
        )
        return _get_azure_blob_storage_provider(
            account_name,
            container_name,
            settings.AZURE_STORAGE_MANAGED_IDENTITY_CLIENT_ID,
        )

    raise ConfigurationError(
        [
            ConfigurationIssue(
                "STORAGE_BACKEND",
                "must be one of: azure_blob, local.",
            )
        ]
    )


async def close_storage_providers() -> None:
    for provider in tuple(_azure_blob_storage_providers):
        await provider.aclose()
        _azure_blob_storage_providers.remove(provider)

    _get_local_storage_provider.cache_clear()
    _get_azure_blob_storage_provider.cache_clear()


@lru_cache
def _get_local_storage_provider(storage_root: str) -> LocalStorageProvider:
    return LocalStorageProvider(storage_root)


@lru_cache
def _get_azure_blob_storage_provider(
    account_name: str,
    container_name: str,
    managed_identity_client_id: str | None,
) -> AzureBlobStorageProvider:
    provider = AzureBlobStorageProvider(
        account_name=account_name,
        container_name=container_name,
        managed_identity_client_id=managed_identity_client_id,
    )
    _azure_blob_storage_providers.add(provider)
    return provider


def _require_azure_storage_config(value: str | None, name: str) -> str:
    if value is None or not value.strip():
        raise ConfigurationError(
            [
                ConfigurationIssue(
                    name,
                    "is required when STORAGE_BACKEND=azure_blob.",
                )
            ]
        )
    return value.strip()


_azure_blob_storage_providers: set[AzureBlobStorageProvider] = set()
_bearer_scheme = HTTPBearer(auto_error=False)


def get_external_identity(
    settings: Annotated[Settings, Depends(get_settings)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ],
) -> ExternalIdentity:
    return validate_bearer_token(
        token=credentials.credentials if credentials is not None else None,
        settings=settings,
    )


def get_file_metadata_repository(
    _identity: Annotated[ExternalIdentity, Depends(get_external_identity)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> FileMetadataRepository:
    return SQLAlchemyFileMetadataRepository(session)


def get_document_repository(
    _identity: Annotated[ExternalIdentity, Depends(get_external_identity)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> DocumentRepository:
    return SQLAlchemyDocumentRepository(session)


def get_conversation_repository(
    _identity: Annotated[ExternalIdentity, Depends(get_external_identity)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ConversationRepository:
    return SQLAlchemyConversationRepository(session)


def get_workflow_execution_repository(
    _identity: Annotated[ExternalIdentity, Depends(get_external_identity)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> WorkflowExecutionRepository:
    return SQLAlchemyWorkflowExecutionRepository(session)


def get_user_repository(
    _identity: Annotated[ExternalIdentity, Depends(get_external_identity)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepository:
    return SQLAlchemyUserRepository(session)


async def get_current_principal(
    identity: Annotated[ExternalIdentity, Depends(get_external_identity)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthenticatedPrincipal:
    user = await user_repository.resolve_external_identity(identity)
    if not user.is_active:
        raise AppException(
            "User is inactive.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="USER_INACTIVE",
        )
    return AuthenticatedPrincipal(
        user_id=user.id,
        issuer=identity.issuer,
        subject=identity.subject,
        email=user.email,
        display_name=user.display_name,
    )


def get_upload_service(
    settings: Annotated[Settings, Depends(get_settings)],
    storage_provider: Annotated[StorageProvider, Depends(get_storage_provider)],
    document_repository: Annotated[
        DocumentRepository,
        Depends(get_document_repository),
    ],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
) -> UploadService:
    return UploadService(
        storage_provider=storage_provider,
        document_repository=document_repository,
        user_id=principal.user_id,
        storage_backend=settings.STORAGE_BACKEND,
        max_upload_bytes=settings.MAX_UPLOAD_BYTES,
    )


def get_document_ingestion_service(
    settings: Annotated[Settings, Depends(get_settings)],
    storage_provider: Annotated[StorageProvider, Depends(get_storage_provider)],
    document_repository: Annotated[
        DocumentRepository,
        Depends(get_document_repository),
    ],
) -> DocumentIngestionService:
    return SynchronousDocumentIngestionService(
        storage_provider=storage_provider,
        document_repository=document_repository,
        indexer_factory=lambda loader: _build_document_indexer(settings, loader),
    )


def get_document_service(
    upload_service: Annotated[UploadService, Depends(get_upload_service)],
    document_repository: Annotated[
        DocumentRepository,
        Depends(get_document_repository),
    ],
    ingestion_service: Annotated[
        DocumentIngestionService,
        Depends(get_document_ingestion_service),
    ],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
) -> DocumentService:
    return StoredDocumentService(
        upload_service=upload_service,
        document_repository=document_repository,
        ingestion_service=ingestion_service,
        user_id=principal.user_id,
    )


def get_workflow_status_service(
    workflow_repository: Annotated[
        WorkflowExecutionRepository,
        Depends(get_workflow_execution_repository),
    ],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
) -> WorkflowStatusService:
    return RepositoryWorkflowStatusService(
        workflow_repository,
        user_id=principal.user_id,
    )


def get_conversation_history_builder(
    settings: Annotated[Settings, Depends(get_settings)],
    conversation_repository: Annotated[
        ConversationRepository,
        Depends(get_conversation_repository),
    ],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
) -> ConversationHistoryBuilder:
    return ConversationHistoryBuilder(
        conversation_repository,
        user_id=principal.user_id,
        max_turns=settings.CONVERSATION_HISTORY_MAX_TURNS,
        max_chars=settings.CONVERSATION_HISTORY_MAX_CHARS,
    )


def get_conversation_service(
    conversation_repository: Annotated[
        ConversationRepository,
        Depends(get_conversation_repository),
    ],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
) -> ConversationService:
    return RepositoryConversationService(
        conversation_repository,
        user_id=principal.user_id,
    )


def ensure_core_document_capabilities_registered() -> None:
    skill = DocumentProcessingSkill()
    registry = get_runtime_skill_registry()
    if registry.get(skill.name) is not None:
        return

    register_skill(skill)


def get_agent_graph(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AgentGraphInvoker:
    ensure_core_document_capabilities_registered()
    return create_agent_graph(settings=settings)


def get_question_answering_service(
    settings: Annotated[Settings, Depends(get_settings)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    workflow_repository: Annotated[
        WorkflowExecutionRepository,
        Depends(get_workflow_execution_repository),
    ],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
) -> QuestionAnsweringService:
    embedding_provider = OpenAIEmbeddingProvider(settings=settings)
    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=_get_qdrant_vector_store(settings, embedding_provider.dimension),
    )
    return RAGQuestionAnsweringService(
        retriever=retriever,
        context_builder=ContextBuilder(max_chars=settings.RAG_CONTEXT_MAX_CHARS),
        response_generator=OpenAIResponseGenerator(settings=settings),
        document_service=document_service,
        workflow_repository=workflow_repository,
        user_id=principal.user_id,
        top_k=settings.RAG_RETRIEVAL_TOP_K,
    )


def get_routed_question_answering_service(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    workflow_repository: Annotated[
        WorkflowExecutionRepository,
        Depends(get_workflow_execution_repository),
    ],
    direct_question_service: Annotated[
        QuestionAnsweringService,
        Depends(get_question_answering_service),
    ],
    agent_graph: Annotated[AgentGraphInvoker, Depends(get_agent_graph)],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
) -> QuestionAnsweringService:
    return RoutedQuestionAnsweringService(
        direct_question_service=direct_question_service,
        workflow_repository=workflow_repository,
        document_service=document_service,
        agent_graph=agent_graph,
        user_id=principal.user_id,
    )


def get_message_submission_service(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    question_service: Annotated[
        QuestionAnsweringService,
        Depends(get_routed_question_answering_service),
    ],
    conversation_repository: Annotated[
        ConversationRepository,
        Depends(get_conversation_repository),
    ],
    history_builder: Annotated[
        ConversationHistoryBuilder,
        Depends(get_conversation_history_builder),
    ],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
) -> MessageSubmissionService:
    return MessageSubmissionService(
        document_service=document_service,
        question_service=question_service,
        conversation_repository=conversation_repository,
        history_builder=history_builder,
        user_id=principal.user_id,
    )


def _get_qdrant_vector_store(
    settings: Settings,
    dimension: int,
) -> QdrantVectorStore:
    try:
        return QdrantVectorStore(settings=settings, dimension=dimension)
    except VectorStoreError as exc:
        if settings.QDRANT_URL is None or not settings.QDRANT_URL.strip():
            message = (
                "Question-answering service is unavailable because Qdrant is not "
                "configured. Set QDRANT_URL before retrying."
            )
        else:
            message = (
                "Question-answering service is unavailable because Qdrant is "
                "unavailable or misconfigured. Check Qdrant configuration before "
                "retrying."
            )
        raise QuestionAnsweringUnavailableError(message) from exc


def _build_document_indexer(
    settings: Settings,
    loader: DocumentLoader,
) -> DocumentIndexer:
    embedding_provider = OpenAIEmbeddingProvider(settings=settings)
    return DocumentIndexer(
        loader=loader,
        chunker=RecursiveTextChunker(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
        ),
        embedding_provider=embedding_provider,
        vector_store=QdrantVectorStore(
            settings=settings,
            dimension=embedding_provider.dimension,
            wait=True,
        ),
    )
