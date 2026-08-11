"""File guide.

- Use: Defines generic deterministic runtime executor contracts.
- Usage: Import Tool and ToolDefinition from openagentlab.tools.base.
- Duties: Keeps runtime executors independent from LangGraph and provider SDKs.
- Depends on: External packages: typing. Project modules:
  openagentlab.skills.capabilities.
"""

from typing import Any, Protocol

from openagentlab.skills.capabilities import CapabilityPromptView

ToolDefinition = CapabilityPromptView


class Tool(Protocol):
    def execute(self, **kwargs: Any) -> Any:
        """Run a deterministic operation."""
