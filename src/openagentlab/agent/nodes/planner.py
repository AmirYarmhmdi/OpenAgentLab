"""File guide.

- Use: Defines the LangGraph planner node wrapper.
- Usage: Import create_planner_node or planner_node from
  openagentlab.agent.nodes.planner.
- Duties: Calls an injected planner and writes serializable state updates.
- Depends on: Project modules: openagentlab.agent.exceptions,
  openagentlab.agent.planner, and openagentlab.agent.state.
"""

from collections.abc import Callable
from typing import Any

from openagentlab.agent.exceptions import PlannerError
from openagentlab.agent.planner import OpenAIPlanner, Planner
from openagentlab.agent.schemas import ExecutionPlan
from openagentlab.agent.state import AgentState
from openagentlab.tools.registry import get_tool_definitions


def create_planner_node(planner: Planner) -> Callable[[AgentState], dict[str, Any]]:
    def _planner_node(state: AgentState) -> dict[str, Any]:
        return planner_node(state, planner=planner)

    return _planner_node


def planner_node(
    state: AgentState, *, planner: Planner | None = None
) -> dict[str, Any]:
    user_query = state.get("user_query", "")
    if not user_query.strip():
        return {
            "execution_plan": ExecutionPlan(),
            "plan": [],
            "requires_tool": False,
            "error": "Planner requires a non-empty user_query.",
        }

    active_planner = planner or OpenAIPlanner()

    try:
        execution_plan = active_planner.create_plan(
            user_query=user_query,
            available_capabilities=get_tool_definitions(),
        )
    except PlannerError as exc:
        return {
            "execution_plan": ExecutionPlan(),
            "plan": [],
            "requires_tool": False,
            "error": str(exc),
        }
    except Exception:
        return {
            "execution_plan": ExecutionPlan(),
            "plan": [],
            "requires_tool": False,
            "error": "Planner failed unexpectedly.",
        }

    return {
        "execution_plan": execution_plan,
        "plan": _legacy_plan_steps(execution_plan),
        "requires_tool": bool(execution_plan.tasks),
        "error": None,
    }


def _legacy_plan_steps(execution_plan: ExecutionPlan) -> list[str]:
    return [f"{task.id}: {task.capability}" for task in execution_plan.tasks]
