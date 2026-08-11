"""File guide.

- Use: Exports the public Skill framework objects.
- Usage: Import from openagentlab.skills.__init__ to use the package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.skills.base,
  openagentlab.skills.registry, and openagentlab.skills.tool.
"""

from openagentlab.skills.base import BaseSkill, SkillMetadata
from openagentlab.skills.capabilities import CapabilityDefinition, CapabilityPromptView
from openagentlab.skills.registry import SkillRegistry
from openagentlab.skills.tool import BaseTool

__all__ = [
    "BaseSkill",
    "BaseTool",
    "CapabilityDefinition",
    "CapabilityPromptView",
    "SkillMetadata",
    "SkillRegistry",
]
