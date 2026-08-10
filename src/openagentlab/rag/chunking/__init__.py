"""File guide.

- Use: Exports text chunking contracts and implementations.
- Usage: Import from openagentlab.rag.chunking.__init__ to use the package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.rag.chunking.base, and
  openagentlab.rag.chunking.recursive.
"""

from openagentlab.rag.chunking.base import TextChunker
from openagentlab.rag.chunking.recursive import (
    RecursiveChunkerConfig,
    RecursiveTextChunker,
)

__all__ = ["RecursiveChunkerConfig", "RecursiveTextChunker", "TextChunker"]
