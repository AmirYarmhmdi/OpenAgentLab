"""File guide.

- Use: Runs query embedding and vector search to retrieve matching chunks.
- Usage: Import Retriever from openagentlab.rag.retrieval.retriever.
- Duties: Defines Retriever and related helper logic.
- Depends on: Project modules: openagentlab.rag.embeddings.base,
  openagentlab.rag.exceptions, openagentlab.rag.models, and
  openagentlab.rag.vectorstores.base.
"""

from openagentlab.rag.embeddings.base import EmbeddingProvider
from openagentlab.rag.exceptions import RetrieverError
from openagentlab.rag.models import RetrievedChunk
from openagentlab.rag.vectorstores.base import MetadataFilter, VectorStore


class Retriever:
    """Embed a query and retrieve relevant chunks from a vector store."""

    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: MetadataFilter | None = None,
        score_threshold: float | None = None,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            msg = "Retrieval query must not be empty."
            raise RetrieverError(msg)
        if top_k <= 0:
            msg = "top_k must be greater than zero."
            raise RetrieverError(msg)

        query_embedding = self._embedding_provider.embed_query(query)
        return self._vector_store.search(
            query_embedding,
            top_k=top_k,
            filters=filters,
            score_threshold=score_threshold,
        )
