"""File guide.

- Use: Exports document loader contracts and implementations.
- Usage: Import from openagentlab.rag.loaders.__init__ to use the package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.rag.loaders.base,
  openagentlab.rag.loaders.pdf, and openagentlab.rag.loaders.text.
"""

from openagentlab.rag.loaders.base import DocumentLoader
from openagentlab.rag.loaders.pdf import PDFLoader
from openagentlab.rag.loaders.text import TextFileLoader

__all__ = ["DocumentLoader", "PDFLoader", "TextFileLoader"]
