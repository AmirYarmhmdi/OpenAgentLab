"""File guide.

- Use: Exports embedding provider contracts and implementations.
- Usage: Import from openagentlab.rag.embeddings.__init__ to use the package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.rag.embeddings.base, and
  openagentlab.rag.embeddings.openai.
"""

from openagentlab.rag.embeddings.base import EmbeddingProvider
from openagentlab.rag.embeddings.openai import (
    OpenAIEmbeddingConfig,
    OpenAIEmbeddingProvider,
)

__all__ = ["EmbeddingProvider", "OpenAIEmbeddingConfig", "OpenAIEmbeddingProvider"]
