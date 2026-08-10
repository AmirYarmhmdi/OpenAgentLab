"""File guide.

- Use: Exports retrieval helpers.
- Usage: Import from openagentlab.rag.retrieval.__init__ to use the package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.rag.retrieval.retriever.
"""

from openagentlab.rag.retrieval.retriever import Retriever

__all__ = ["Retriever"]
