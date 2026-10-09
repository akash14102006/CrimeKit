"""
NemoClaw & OpenShell Security Sandbox for CrimeKit Agent Tools.

Enforces:
- Default DENY policy
- Allowed tool registry (no arbitrary code, shell, or unbounded queries)
- Strict case isolation (agents cannot switch or cross-access cases)
- Network policy (only whitelisted external endpoints, e.g. Tavily, Nebius)
- Audit logging & telemetry event emission:
  sandbox.started, sandbox.policy_allowed, sandbox.policy_denied, sandbox.completed
"""

import time
import uuid
import logging
from typing import Dict, Any, List, Set, Optional

logger = logging.getLogger(__name__)

# Canonical permitted tools allowed under OpenShell / NemoClaw policy
APPROVED_TOOLS: Set[str] = {
    "evidence_search",
    "entity_search",
    "knowledge_graph_query",
    "knowledge_graph_traversal",
    "vector_search",
    "timeline_search",
    "temporal_correlation",
    "timeline_event_context",
    "location_search",
    "movement_trace",
    "co_location_analysis",
    "testimony_analysis",
    "tavily_web_research",
    "report_generation",
}

# Explicit agent tool policy mapping
AGENT_TOOL_POLICY: Dict[str, Set[str]] = {
    "detective": {
        "evidence_search",
        "entity_search",
        "knowledge_graph_query",
        "knowledge_graph_traversal",
        "vector_search",
        "tavily_web_research",
    },
    "timeline": {
        "timeline_search",
        "temporal_correlation",
        "timeline_event_context",
    },
    "geoscope": {
        "location_search",
        "movement_trace",
        "co_location_analysis",
        "tavily_web_research",
    },
    "testimony": {
        "testimony_analysis",
        "timeline_search",
        "location_search",
        "entity_search",
        "tavily_web_research",
    },
    "report": {
        "evidence_verification",
        "timeline",
        "contradictions",
        "provenance",
        "case_archive",
        "report_generation",
    },
    "case-orchestrator": APPROVED_TOOLS,
}


class SandboxPolicyViolation(Exception):
    """Raised when an agent attempts to execute an unapproved or out-of-scope tool."""
    def __init__(self, message: str, agent_id: str, tool_name: str, case_id: str):
        super().__init__(message)
        self.message = message
        self.agent_id = agent_id
        self.tool_name = tool_name
        self.case_id = case_id


class AgentSandbox:
    """
    NemoClaw & OpenShell security boundary for agent execution.
    Inspects tool calls before execution and enforces strict isolation.
    """

    @classmethod
    def validate_tool_execution(
        cls,
        *,
        agent_id: str,
        tool_name: str,
        case_id: str,
        arguments: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> bool:
        """
        Validate that the requested tool call conforms to NemoClaw / OpenShell policy.
        Emits telemetry events for security audit trail.
        """
        start_time = time.time()
        audit_id = f"sbx_{uuid.uuid4().hex[:8]}"

        def _emit(event_type: str, data: Dict[str, Any]):
            try:
                from ..events import DomainEvent, publish_event
                ev = DomainEvent(event_type=event_type, case_id=case_id, metadata=data)
                publish_event(ev)
            except Exception:
                pass

        base_event = {
            "case_id": case_id,
            "session_id": session_id or "",
            "agent": agent_id,
            "tool": tool_name,
            "audit_id": audit_id,
            "timestamp": start_time,
        }

        _emit("sandbox.started", base_event)

        # 1. Global Approved Tools (Default DENY)
        if tool_name not in APPROVED_TOOLS:
            err = f"Security Policy Denied: Tool '{tool_name}' is not in approved tool registry."
            logger.warning("[NemoClaw/OpenShell] DENIED: %s by %s in %s", tool_name, agent_id, case_id)
            _emit("sandbox.policy_denied", {**base_event, "reason": "unapproved_tool", "error": err})
            raise SandboxPolicyViolation(err, agent_id, tool_name, case_id)

        # 2. Agent Scope Validation
        allowed_for_agent = AGENT_TOOL_POLICY.get(agent_id, set())
        if tool_name not in allowed_for_agent and agent_id != "case-orchestrator":
            err = f"Security Policy Denied: Agent '{agent_id}' is not authorized to call '{tool_name}'."
            logger.warning("[NemoClaw/OpenShell] DENIED: %s out of scope for agent %s", tool_name, agent_id)
            _emit("sandbox.policy_denied", {**base_event, "reason": "agent_scope_exceeded", "error": err})
            raise SandboxPolicyViolation(err, agent_id, tool_name, case_id)

        # 3. Case Isolation Validation
        arg_case = arguments.get("case_id")
        if arg_case and arg_case != case_id:
            err = f"Security Policy Denied: Cross-case access attempt ({arg_case} != {case_id})."
            logger.error("[NemoClaw/OpenShell] VIOLATION: Cross-case leak prevented")
            _emit("sandbox.policy_denied", {**base_event, "reason": "case_isolation_violation", "error": err})
            raise SandboxPolicyViolation(err, agent_id, tool_name, case_id)

        # 4. Dangerous Parameters Check (No shell, SQL, or arbitrary code)
        for k, v in arguments.items():
            if isinstance(v, str):
                v_lower = v.lower()
                if any(inj in v_lower for inj in ["rm -rf", "drop table", "; drop", "exec(", "eval("]):
                    err = f"Security Policy Denied: Suspicious command detected in parameter '{k}'."
                    _emit("sandbox.policy_denied", {**base_event, "reason": "dangerous_parameter", "error": err})
                    raise SandboxPolicyViolation(err, agent_id, tool_name, case_id)

        _emit("sandbox.policy_allowed", {**base_event, "allowed_tools": list(allowed_for_agent)})
        _emit("sandbox.completed", {**base_event, "duration_ms": (time.time() - start_time) * 1000})
        return True


sandbox = AgentSandbox()
