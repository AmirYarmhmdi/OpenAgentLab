"""File guide.

- Use: Exports the main RAG pipeline classes and models.
- Usage: Import from openagentlab.rag.__init__ to use the package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.rag.chunking.recursive,
  openagentlab.rag.context.builder, openagentlab.rag.indexing,
  openagentlab.rag.loaders.pdf, openagentlab.rag.loaders.text, and 2 more.
"""

from openagentlab.rag.chunking.recursive import (
    RecursiveChunkerConfig,
    RecursiveTextChunker,
)
from openagentlab.rag.context.builder import ContextBuilder, ContextBuilderConfig
from openagentlab.rag.indexing import DocumentIndexer
from openagentlab.rag.loaders.pdf import PDFLoader
from openagentlab.rag.loaders.text import TextFileLoader
from openagentlab.rag.models import BuiltContext, Chunk, Document, RetrievedChunk
from openagentlab.rag.retrieval.retriever import Retriever

__all__ = [
    "BuiltContext",
    "Chunk",
    "ContextBuilder",
    "ContextBuilderConfig",
    "Document",
    "DocumentIndexer",
    "PDFLoader",
    "RecursiveChunkerConfig",
    "RecursiveTextChunker",
    "RetrievedChunk",
    "Retriever",
    "TextFileLoader",
]
