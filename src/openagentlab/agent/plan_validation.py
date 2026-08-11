"""File guide.

- Use: Validates ExecutionPlan objects against canonical capabilities.
- Usage: Import ExecutionPlanValidator from openagentlab.agent.plan_validation.
- Duties: Checks executable capability references without executing tasks.
- Depends on: Project modules: openagentlab.agent.schemas and
  openagentlab.skills.registry.
"""

from openagentlab.agent.schemas import ExecutionPlan
from openagentlab.skills.registry import SkillRegistry


class ExecutionPlanValidationError(ValueError):
    pass


class ExecutionPlanValidator:
    """Validate structured plans against the canonical Skills registry."""

    def validate(
        self,
        plan: ExecutionPlan,
        *,
        skill_registry: SkillRegistry,
    ) -> ExecutionPlan:
        for task in plan.tasks:
            if skill_registry.get_capability(task.capability) is None:
                msg = f"Task references unavailable capability: {task.capability}"
                raise ExecutionPlanValidationError(msg)

        return plan
