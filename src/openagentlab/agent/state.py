"""File guide.

- Use: Defines the semantic state shared across agent workflow nodes.
- Usage: Import AgentState from openagentlab.agent.state.
- Duties: Keeps LangGraph state focused on orchestration data.
- Depends on: External packages: typing. Project modules:
  openagentlab.agent.execution and openagentlab.agent.schemas.
"""

from typing import Any, TypedDict

from openagentlab.agent.execution import ExecutionResult
from openagentlab.agent.schemas import ExecutionPlan


class AgentState(TypedDict, total=False):
    user_query: str
    execution_plan: ExecutionPlan
    execution_result: ExecutionResult
    # Compatibility fields derived from execution_plan/execution_result.
    plan: list[str]
    requires_tool: bool
    selected_tool: str | None
    tool_arguments: dict[str, Any]
    tool_result: Any
    response: str
    error: str | None
