"""File guide.

- Use: Exports the reader tool and schemas for plain text files.
- Usage: Import from
  openagentlab.skills.document_processing.tools.text_reader.__init__ to use the
  package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules:
  openagentlab.skills.document_processing.tools.text_reader.schemas, and
  openagentlab.skills.document_processing.tools.text_reader.tool.
"""

from .schemas import TextReaderInput, TextReaderOutput
from .tool import TextReaderError, TextReaderTool

__all__ = [
    "TextReaderError",
    "TextReaderInput",
    "TextReaderOutput",
    "TextReaderTool",
]
