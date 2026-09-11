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

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from openagentlab.agent.response_generator import OpenAIResponseGenerator
from openagentlab.core.config import Settings, get_settings
from openagentlab.database.session import get_async_session
from openagentlab.rag.context.builder import ContextBuilder
from openagentlab.rag.embeddings.openai import OpenAIEmbeddingProvider
from openagentlab.rag.retrieval.retriever import Retriever
from openagentlab.rag.vectorstores.qdrant import QdrantVectorStore
from openagentlab.repositories.file_metadata import (
    FileMetadataRepository,
    SQLAlchemyFileMetadataRepository,
)
from openagentlab.repositories.workflow_execution import (
    SQLAlchemyWorkflowExecutionRepository,
    WorkflowExecutionRepository,
)
from openagentlab.services.documents import DocumentService, StoredDocumentService
from openagentlab.services.questions import (
    QuestionAnsweringService,
    RAGQuestionAnsweringService,
)
from openagentlab.services.upload import UploadService
from openagentlab.services.workflows import (
    RepositoryWorkflowStatusService,
    WorkflowStatusService,
)
from openagentlab.storage.azure_blob import AzureBlobStorageProvider
from openagentlab.storage.base import StorageProvider
from openagentlab.storage.local import LocalStorageProvider


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

    raise RuntimeError(f"Unsupported storage backend: {settings.STORAGE_BACKEND}")


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
        raise RuntimeError(f"{name} is required when STORAGE_BACKEND=azure_blob.")
    return value.strip()


_azure_blob_storage_providers: set[AzureBlobStorageProvider] = set()


def get_file_metadata_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> FileMetadataRepository:
    return SQLAlchemyFileMetadataRepository(session)


def get_workflow_execution_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> WorkflowExecutionRepository:
    return SQLAlchemyWorkflowExecutionRepository(session)


def get_upload_service(
    settings: Annotated[Settings, Depends(get_settings)],
    storage_provider: Annotated[StorageProvider, Depends(get_storage_provider)],
    file_metadata_repository: Annotated[
        FileMetadataRepository,
        Depends(get_file_metadata_repository),
    ],
) -> UploadService:
    return UploadService(
        storage_provider=storage_provider,
        file_metadata_repository=file_metadata_repository,
        storage_backend=settings.STORAGE_BACKEND,
    )


def get_document_service(
    upload_service: Annotated[UploadService, Depends(get_upload_service)],
    file_metadata_repository: Annotated[
        FileMetadataRepository,
        Depends(get_file_metadata_repository),
    ],
) -> DocumentService:
    return StoredDocumentService(
        upload_service=upload_service,
        file_metadata_repository=file_metadata_repository,
    )


def get_workflow_status_service(
    workflow_repository: Annotated[
        WorkflowExecutionRepository,
        Depends(get_workflow_execution_repository),
    ],
) -> WorkflowStatusService:
    return RepositoryWorkflowStatusService(workflow_repository)


def get_question_answering_service(
    settings: Annotated[Settings, Depends(get_settings)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    workflow_repository: Annotated[
        WorkflowExecutionRepository,
        Depends(get_workflow_execution_repository),
    ],
) -> QuestionAnsweringService:
    embedding_provider = OpenAIEmbeddingProvider(settings=settings)
    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=QdrantVectorStore(
            settings=settings,
            dimension=embedding_provider.dimension,
        ),
    )
    return RAGQuestionAnsweringService(
        retriever=retriever,
        context_builder=ContextBuilder(),
        response_generator=OpenAIResponseGenerator(settings=settings),
        document_service=document_service,
        workflow_repository=workflow_repository,
    )
