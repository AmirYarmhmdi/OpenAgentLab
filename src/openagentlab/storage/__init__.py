"""File guide.

- Use: Exports storage provider contracts and implementations.
- Usage: Import from openagentlab.storage.__init__ to use the package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.storage.base, and
  openagentlab.storage.local.
"""

from openagentlab.storage.base import StorageProvider, StoredObject
from openagentlab.storage.local import LocalStorageProvider

__all__ = [
    "LocalStorageProvider",
    "StorageProvider",
    "StoredObject",
]
