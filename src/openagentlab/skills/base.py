"""File guide.

- Use: Defines the shared Skill metadata and base Skill object.
- Usage: Import BaseSkill, and SkillMetadata from openagentlab.skills.base.
- Duties: Defines BaseSkill, and SkillMetadata and related helper logic.
- Depends on: Project modules: openagentlab.skills.tool.
"""

from pydantic import BaseModel, Field

from openagentlab.skills.tool import BaseTool


class SkillMetadata(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    version: str = Field(min_length=1)


class BaseSkill:
    metadata: SkillMetadata
    instructions: str
    capabilities: tuple[str, ...]
    dependencies: tuple[str, ...]
    tools: tuple[BaseTool, ...]

    def __init__(
        self,
        *,
        metadata: SkillMetadata,
        instructions: str,
        capabilities: tuple[str, ...] = (),
        dependencies: tuple[str, ...] = (),
        tools: tuple[BaseTool, ...] = (),
    ) -> None:
        self.metadata = metadata
        self.instructions = instructions
        self.capabilities = capabilities
        self.dependencies = dependencies
        self.tools = tools

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def executable_capabilities(self) -> tuple[str, ...]:
        return tuple(tool.capability for tool in self.tools)

    def get_tool(self, name: str) -> BaseTool | None:
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
