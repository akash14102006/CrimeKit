"""
Investigation Tool Registry for CrimeKit.

Manages registration, lookup, permission checking, argument validation,
and execution dispatch for all controlled investigation tools.
"""

import time
import uuid
import logging
from typing import Dict, List, Optional, Any

from .base import BaseInvestigationTool, ToolResult, ToolDefinition

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    def __init__(self, message: str, tool_name: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.tool_name = tool_name
        self.status_code = status_code


class InvestigationToolRegistry:
    """
    Central CrimeKit investigation tool registry.
    Strictly forbids arbitrary code, SQL, Cypher, shell, or unbounded calls.
    """

    def __init__(self):
        self._tools: Dict[str, BaseInvestigationTool] = {}

    def register(self, tool: BaseInvestigationTool) -> None:
        """Register a controlled tool."""
        self._tools[tool.tool_name] = tool
        logger.info("Registered investigation tool: %s", tool.tool_name)

    def get(self, tool_name: str) -> Optional[BaseInvestigationTool]:
        """Retrieve tool by name."""
        if tool_name == "knowledge_graph_query":
            return self._tools.get("knowledge_graph_traversal")
        return self._tools.get(tool_name)

    def list_tools(self) -> List[BaseInvestigationTool]:
        """List all registered tools."""
        return list(self._tools.values())

    def get_tool_definitions(self, agent_id: Optional[str] = None) -> List[ToolDefinition]:
        """Return definitions for tools, optionally filtered by agent scope."""
        tools = self.get_tools_for_agent(agent_id) if agent_id else self.list_tools()
        return [t.get_tool_definition() for t in tools]

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible tool specifications for all tools."""
        return [t.to_openai_tool() for t in self._tools.values()]

    def get_openai_tools_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible tool specifications scoped to a specific specialist agent."""
        tools = self.get_tools_for_agent(agent_id)
        return [t.to_openai_tool() for t in tools]

    def get_tools_for_agent(self, agent_id: str) -> List[BaseInvestigationTool]:
        """
        Return the tools authorized for a specific agent.
        Prevents specialist agents from invoking out-of-scope tools.
        """
        agent_tool_map = {
            "detective": ["evidence_search", "entity_search", "knowledge_graph_traversal", "vector_search", "tavily_web_research"],
            "timeline": ["timeline_search", "temporal_correlation", "timeline_event_context"],
            "geoscope": ["location_search", "movement_trace", "co_location_analysis", "tavily_web_research"],
            "testimony": ["testimony_analysis", "timeline_search", "location_search", "entity_search", "tavily_web_research"],
        }
        allowed_names = agent_tool_map.get(agent_id)
        if allowed_names is None:
            # For general agents or unspecified, return all registered tools
            return list(self._tools.values())
        return [self._tools[name] for name in allowed_names if name in self._tools]

    async def execute(
        self,
        tool_name: str,
        *,
        case_id: str,
        user_id: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """
        Validate, dispatch, and monitor execution of a tool.
        Enforces NemoClaw / OpenShell security policy and case isolation.
        """
        exec_id = f"exec_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        agent_id = (context or {}).get("agent", "detective")
        session_id = (context or {}).get("session_id", "")

        # ── NemoClaw / OpenShell Security Boundary ──
        try:
            from ...security.agent_sandbox import sandbox, SandboxPolicyViolation
            sandbox.validate_tool_execution(
                agent_id=agent_id,
                tool_name=tool_name,
                case_id=case_id,
                arguments=arguments,
                session_id=session_id,
            )
        except SandboxPolicyViolation as pol_err:
            logger.warning("[NemoClaw/OpenShell] Policy denied tool execution: %s", pol_err.message)
            return ToolResult(
                tool_name=tool_name,
                execution_id=exec_id,
                status="failed",
                error_message=f"Tool '{tool_name}' is not recognized or permitted: {pol_err.message}",
                duration_ms=(time.time() - start_time) * 1000,
            )

        tool = self.get(tool_name)
        if not tool:
            logger.warning("Attempted execution of unregistered tool: %s", tool_name)
            return ToolResult(
                tool_name=tool_name,
                execution_id=exec_id,
                status="failed",
                error_message=f"Tool '{tool_name}' is not recognized or permitted.",
                duration_ms=(time.time() - start_time) * 1000,
            )

        # Enforce that model cannot override case_id or user_id
        safe_args = dict(arguments or {})
        safe_args.pop("case_id", None)
        safe_args.pop("user_id", None)

        try:
            logger.info(
                "Executing investigation tool",
                extra={
                    "tool": tool_name,
                    "case_id": case_id,
                    "user_id": user_id,
                    "execution_id": exec_id,
                },
            )

            result = await tool.execute(
                case_id=case_id,
                user_id=user_id,
                arguments=safe_args,
                context=context,
            )
            result.execution_id = exec_id
            return result

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "Investigation tool execution failed",
                exc_info=True,
                extra={
                    "tool": tool_name,
                    "case_id": case_id,
                    "execution_id": exec_id,
                },
            )
            return ToolResult(
                tool_name=tool_name,
                execution_id=exec_id,
                status="failed",
                error_message=f"Execution error in {tool_name}: {str(exc)[:150]}",
                duration_ms=round(duration_ms, 2),
            )


# Default singleton instance of tool registry
default_tool_registry = InvestigationToolRegistry()


def get_tool_registry() -> InvestigationToolRegistry:
    return default_tool_registry
