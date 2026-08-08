from openagentlab.skills.base import BaseSkill


class DuplicateSkillError(ValueError):
    pass


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        if skill.name in self._skills:
            msg = f"Skill already registered: {skill.name}"
            raise DuplicateSkillError(msg)

        self._skills[skill.name] = skill

    def get(self, name: str) -> BaseSkill | None:
        return self._skills.get(name)

    def list_skills(self) -> tuple[BaseSkill, ...]:
        return tuple(self._skills.values())

    def find_by_capability(self, capability: str) -> tuple[BaseSkill, ...]:
        """Find skills that declare a capability, regardless of executable tools."""
        return tuple(
            skill for skill in self._skills.values() if capability in skill.capabilities
        )
