"""File guide.

- Use: Builds the LangGraph workflow for deterministic plan execution.
- Usage: Import create_agent_graph from openagentlab.agent.graph.
- Duties: Wires planner, deterministic plan execution, and response generation.
- Depends on: External packages: langgraph. Project modules:
  openagentlab.agent.nodes, openagentlab.agent.state, and
  openagentlab.observability.
"""

from typing import Any

from langgraph.graph import END, START, StateGraph

import openagentlab.observability as observability
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
from openagentlab.core.config import Settings


def create_agent_graph(
    *,
    planner: Planner | None = None,
    tool_selector: ToolSelector | None = None,
    execution_plan_executor: ExecutionPlanExecutor | None = None,
    response_generator: ResponseGenerator | None = None,
    settings: Settings | None = None,
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

    return ObservableAgentGraph(builder.compile(), settings=settings)


class ObservableAgentGraph:
    """Thin wrapper that adds trace config at the graph invocation boundary."""

    def __init__(self, graph: Any, *, settings: Settings | None = None) -> None:
        self._graph = graph
        self._settings = settings

    def invoke(
        self,
        input: Any,
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        workflow_metadata = _workflow_metadata(self._settings)
        with observability.observed_workflow(
            name="agent.workflow",
            input=input,
            metadata=workflow_metadata,
            settings=self._settings,
        ) as observation:
            result = self._graph.invoke(
                input,
                config=observability.with_langgraph_callbacks(
                    config,
                    settings=self._settings,
                ),
                **kwargs,
            )
            observation.update(output=observability.sanitize_for_observability(result))
            return result

    def __getattr__(self, name: str) -> Any:
        return getattr(self._graph, name)


def _workflow_metadata(settings: Settings | None) -> dict[str, str]:
    if settings is None:
        return {"component": "agent"}
    return {
        "component": "agent",
        "environment": settings.ENVIRONMENT,
        "app_version": settings.APP_VERSION,
    }
