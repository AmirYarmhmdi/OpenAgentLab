"""File guide.

- Use: Defines the base class for deterministic tools owned by Skills.
- Usage: Import BaseTool from openagentlab.skills.tool.
- Duties: Defines BaseTool and related helper logic.
- Depends on: External packages: abc, pydantic. Project modules:
  openagentlab.skills.capabilities.

Note: BaseTool lives under openagentlab.skills because current tools are owned
by Skills. A future top-level tools package can be added when generic tools are
needed.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from openagentlab.skills.capabilities import CapabilityDefinition


class BaseTool(ABC):
    name: str
    description: str
    capability: str
    args_schema: type[BaseModel]

    def __init__(
        self,
        *,
        name: str,
        description: str,
        capability: str,
        args_schema: type[BaseModel],
    ) -> None:
        self.name = name
        self.description = description
        self.capability = capability
        self.args_schema = args_schema

    @property
    def capability_definition(self) -> CapabilityDefinition:
        return CapabilityDefinition(
            name=self.capability,
            description=self.description,
            input_schema=self.args_schema,
        )

    @abstractmethod
    def execute(self, tool_input: object) -> object:
        """Run the deterministic operation for this tool."""
