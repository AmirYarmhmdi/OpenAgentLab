"""File guide.

- Use: Defines the deterministic tool execution node.
- Usage: Import tool_execution_node from openagentlab.agent.nodes.tool_execution.
- Duties: Resolves and executes registered tools, returning result or error.
- Depends on: Project modules: openagentlab.agent.state and
  openagentlab.tools.registry.
"""

from typing import Any

from openagentlab.agent.state import AgentState
from openagentlab.tools.registry import UnknownToolError, get_tool


def tool_execution_node(state: AgentState) -> dict[str, Any]:
    selected_tool = state.get("selected_tool")
    if not selected_tool:
        return {}

    tool_arguments = state.get("tool_arguments", {})

    try:
        tool = get_tool(selected_tool)
        return {"tool_result": tool.execute(**tool_arguments), "error": None}
    except UnknownToolError as exc:
        return {"error": str(exc)}
    except Exception as exc:
        return {"error": f"Tool execution failed for {selected_tool}: {exc}"}
