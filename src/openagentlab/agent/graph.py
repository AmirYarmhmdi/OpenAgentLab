"""File guide.

- Use: Builds the LangGraph workflow for deterministic plan execution.
- Usage: Import create_agent_graph from openagentlab.agent.graph.
- Duties: Wires planner, deterministic plan execution, and response generation.
- Depends on: External packages: langgraph. Project modules:
  openagentlab.agent.nodes and openagentlab.agent.state.
"""

from langgraph.graph import END, START, StateGraph

from openagentlab.agent.execution import ExecutionPlanExecutor
from openagentlab.agent.nodes import (
    create_execute_plan_node,
    create_planner_node,
    create_response_generation_node,
)
from openagentlab.agent.planner import OpenAIPlanner, Planner
from openagentlab.agent.response_generator import (
    OpenAIResponseGenerator,
    ResponseGenerator,
)
from openagentlab.agent.state import AgentState
from openagentlab.agent.tool_selector import ToolSelector


def create_agent_graph(
    *,
    planner: Planner | None = None,
    tool_selector: ToolSelector | None = None,
    execution_plan_executor: ExecutionPlanExecutor | None = None,
    response_generator: ResponseGenerator | None = None,
):
    builder = StateGraph(AgentState)
    resolved_planner = planner or OpenAIPlanner()
    # Keep the legacy selector parameter for compatibility, but do not place it on
    # the ExecutionPlan path.
    _ = tool_selector
    resolved_executor = execution_plan_executor or ExecutionPlanExecutor()
    resolved_response_generator = response_generator or OpenAIResponseGenerator()

    builder.add_node("planner", create_planner_node(resolved_planner))
    builder.add_node("execute_plan", create_execute_plan_node(resolved_executor))
    builder.add_node(
        "response_generation",
        create_response_generation_node(resolved_response_generator),
    )

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "execute_plan")
    builder.add_edge("execute_plan", "response_generation")
    builder.add_edge("response_generation", END)

    return builder.compile()
