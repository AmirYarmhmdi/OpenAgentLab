"""File guide.

- Use: Defines the document loader contract for the RAG pipeline.
- Usage: Import DocumentLoader from openagentlab.rag.loaders.base.
- Duties: Defines DocumentLoader and related helper logic.
- Depends on: Project modules: openagentlab.rag.models.
"""

from pathlib import Path
from typing import Protocol

from openagentlab.rag.models import Document


class DocumentLoader(Protocol):
    """Load and normalize source files into RAG documents."""

    def load(self, path: str | Path) -> list[Document]:
        """Load one logical input into one or more normalized documents."""
