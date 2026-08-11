"""File guide.

- Use: Exposes the initial LangGraph agent orchestration foundation.
- Usage: Import create_agent_graph from openagentlab.agent.
- Duties: Keeps agent orchestration imports short and stable.
- Depends on: Project modules: openagentlab.agent.graph.
"""

from openagentlab.agent.graph import create_agent_graph

__all__ = ("create_agent_graph",)
