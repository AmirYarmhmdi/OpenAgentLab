"""File guide.

- Use: Indexes documents by loading, chunking, embedding, and storing chunks.
- Usage: Import DocumentIndexer from openagentlab.rag.indexing.
- Duties: Defines DocumentIndexer and related helper logic.
- Depends on: Project modules: openagentlab.rag.chunking.base,
  openagentlab.rag.embeddings.base, openagentlab.rag.exceptions,
  openagentlab.rag.loaders.base, openagentlab.rag.models, and 1 more.
"""

import logging
from pathlib import Path

from openagentlab.rag.chunking.base import TextChunker
from openagentlab.rag.embeddings.base import EmbeddingProvider
from openagentlab.rag.exceptions import EmbeddingError, VectorStoreError
from openagentlab.rag.loaders.base import DocumentLoader
from openagentlab.rag.models import IndexingSummary
from openagentlab.rag.vectorstores.base import VectorStore

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Coordinate deterministic document load, chunk, embed, and index steps."""

    def __init__(
        self,
        *,
        loader: DocumentLoader,
        chunker: TextChunker,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._loader = loader
        self._chunker = chunker
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def index(self, path: str | Path) -> IndexingSummary:
        documents = self._loader.load(path)
        chunks = self._chunker.split(documents)

        if not chunks:
            msg = "Indexing produced no chunks."
            raise VectorStoreError(msg)

        embeddings = self._embedding_provider.embed_documents(
            [chunk.text for chunk in chunks],
        )
        if len(embeddings) != len(chunks):
            msg = (
                "Embedding provider returned a different number of embeddings "
                "than chunks."
            )
            raise EmbeddingError(msg)

        self._vector_store.upsert(chunks, embeddings)

        summary = IndexingSummary(
            document_count=len(documents),
            chunk_count=len(chunks),
            document_ids=tuple(document.id for document in documents),
            chunk_ids=tuple(chunk.id for chunk in chunks),
        )
        logger.info(
            "Document indexing completed",
            extra={
                "document_count": summary.document_count,
                "chunk_count": summary.chunk_count,
            },
        )
        return summary
