"""File guide.

- Use: Defines the base class for deterministic tools owned by Skills.
- Usage: Import BaseTool from openagentlab.skills.tool.
- Duties: Defines BaseTool and related helper logic.
- Depends on: External packages only: abc.

Note: BaseTool lives under openagentlab.skills because current tools are owned
by Skills. A future top-level tools package can be added when generic tools are
needed.
"""

from abc import ABC, abstractmethod


class BaseTool(ABC):
    name: str
    description: str
    capability: str

    def __init__(self, *, name: str, description: str, capability: str) -> None:
        self.name = name
        self.description = description
        self.capability = capability

    @abstractmethod
    def execute(self, tool_input: object) -> object:
        """Run the deterministic operation for this tool."""
