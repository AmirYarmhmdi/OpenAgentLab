"""Skill-owned deterministic tool abstractions.

`BaseTool` intentionally lives under `openagentlab.skills` because all current
tools are owned by Skills. A separate `openagentlab.tools` package would add
another abstraction layer without a current requirement.

If OpenAgentLab later introduces generic tools that do not naturally belong to
a specific Skill, the shared tool infrastructure can be extracted into a
top-level `openagentlab.tools` package at that time.
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
