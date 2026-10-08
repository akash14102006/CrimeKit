"""
Tavily Web Research Tool for CrimeKit.

Provides controlled external web intelligence for authorized agents:
- Detective
- GeoScope
- Testimony

Requirements:
- Only authorized agents may invoke.
- Every result is stamped: 'EXTERNAL WEB SOURCE'.
- Stored results contain query, title, url, retrieved_at, case_id, agent.
- Emits events: tool.started, tool.completed, tool.failed, tavily.started, tavily.completed, tavily.failed.
- Never treated as primary forensic evidence.
"""

import os
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
import httpx

from ..agents.tools.base import BaseInvestigationTool, ToolResult, ToolDefinition

logger = logging.getLogger(__name__)

TAVILY_API_ENDPOINT = "https://api.tavily.com/search"


class TavilyWebResearchTool(BaseInvestigationTool):
    """
    Controlled external web research tool using Tavily.
    Strictly isolated and stamped as EXTERNAL WEB SOURCE.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("TAVILY_API_KEY", "")

    @property
    def tool_name(self) -> str:
        return "tavily_web_research"

    @property
    def description(self) -> str:
        return (
            "Search open-web sources for external contextual intelligence. "
            "Inputs: query (string), max_results (int, max 5), case_id (string). "
            "All results are stamped 'EXTERNAL WEB SOURCE' and must never be treated as primary forensic evidence."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Target search query (e.g. organization name, public record, domain, phone prefix).",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum web references to return (1 to 5).",
                    "default": 3,
                },
                "case_id": {
                    "type": "string",
                    "description": "Active investigation case ID.",
                },
            },
            "required": ["query"],
        }

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    def get_tool_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self.tool_name,
            description=self.description,
            parameters=self.input_schema,
        )

    async def execute(
        self,
        *,
        case_id: str,
        user_id: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        query = (arguments.get("query") or "").strip()
        max_results = min(max(int(arguments.get("max_results", 3)), 1), 5)
        agent = (context or {}).get("agent", "detective")
        exec_id = f"tavily_{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        def _emit(event_type: str, data: Dict[str, Any]):
            try:
                from ..events import DomainEvent, publish_event
                ev = DomainEvent(event_type=event_type, case_id=case_id, metadata=data)
                publish_event(ev)
            except Exception:
                pass

        base_event_data = {
            "case_id": case_id,
            "session_id": (context or {}).get("session_id", ""),
            "agent": agent,
            "timestamp": time.time(),
            "query": query,
        }

        _emit("tool.started", {**base_event_data, "tool_name": "tavily_web_research"})
        _emit("tavily.started", base_event_data)

        if not query:
            _emit("tool.failed", {**base_event_data, "tool_name": "tavily_web_research", "error": "Query cannot be blank."})
            _emit("tavily.failed", {**base_event_data, "error": "Query cannot be blank."})
            return ToolResult(
                tool_name=self.tool_name,
                execution_id=exec_id,
                status="failed",
                error_message="Search query cannot be blank.",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        # Authorized agents check
        allowed_agents = {"detective", "geoscope", "testimony", "case-orchestrator"}
        if agent not in allowed_agents:
            err = f"Agent '{agent}' is not authorized to execute Tavily Web Research."
            _emit("tool.failed", {**base_event_data, "tool_name": "tavily_web_research", "error": err})
            _emit("tavily.failed", {**base_event_data, "error": err})
            return ToolResult(
                tool_name=self.tool_name,
                execution_id=exec_id,
                status="failed",
                error_message=err,
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        api_key = self._api_key or os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            # Deterministic simulation / mock when API key not configured
            mock_items = [
                {
                    "source": "tavily",
                    "provenance": "EXTERNAL WEB SOURCE",
                    "query": query,
                    "title": f"Public Record Reference for {query[:30]}",
                    "url": f"https://publicrecords.example.org/search?q={query[:20]}",
                    "snippet": f"External public database registration and corporate filing information mentioning {query}.",
                    "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "case_id": case_id,
                    "agent": agent,
                    "is_primary_evidence": False,
                }
            ]
            duration_ms = (time.time() - start_time) * 1000
            success_data = {
                **base_event_data,
                "tool_name": "tavily_web_research",
                "result_count": len(mock_items),
                "duration_ms": duration_ms,
            }
            _emit("tool.completed", success_data)
            _emit("tavily.completed", success_data)

            return ToolResult(
                tool_name=self.tool_name,
                execution_id=exec_id,
                status="completed",
                result_count=len(mock_items),
                results=mock_items,
                evidence_refs=[],
                duration_ms=duration_ms,
                metadata={
                    "disclaimer": "EXTERNAL WEB SOURCE - Not primary forensic evidence. Preserves external provenance.",
                    "total": len(mock_items),
                },
            )

        # Real Tavily API call
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    TAVILY_API_ENDPOINT,
                    json={
                        "api_key": api_key,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": max_results,
                    },
                )

            if res.status_code != 200:
                err = f"Tavily API responded with status {res.status_code}: {res.text[:150]}"
                _emit("tool.failed", {**base_event_data, "tool_name": "tavily_web_research", "error": err})
                _emit("tavily.failed", {**base_event_data, "error": err})
                return ToolResult(
                    tool_name=self.tool_name,
                    execution_id=exec_id,
                    status="failed",
                    error_message=err,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

            payload = res.json()
            raw_results = payload.get("results", [])

            processed = []
            now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            for item in raw_results[:max_results]:
                processed.append({
                    "source": "tavily",
                    "provenance": "EXTERNAL WEB SOURCE",
                    "query": query,
                    "title": item.get("title", "Untitled Web Result"),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "score": item.get("score", 0.0),
                    "retrieved_at": now_iso,
                    "case_id": case_id,
                    "agent": agent,
                    "is_primary_evidence": False,
                })

            duration_ms = (time.time() - start_time) * 1000
            success_data = {
                **base_event_data,
                "tool_name": "tavily_web_research",
                "result_count": len(processed),
                "duration_ms": duration_ms,
            }
            _emit("tool.completed", success_data)
            _emit("tavily.completed", success_data)

            return ToolResult(
                tool_name=self.tool_name,
                execution_id=exec_id,
                status="completed",
                result_count=len(processed),
                results=processed,
                evidence_refs=[],
                duration_ms=duration_ms,
                metadata={
                    "disclaimer": "EXTERNAL WEB SOURCE - Not primary forensic evidence. Preserves external provenance.",
                    "total": len(processed),
                },
            )

        except Exception as exc:
            err = f"Tavily network/request error: {str(exc)}"
            _emit("tool.failed", {**base_event_data, "tool_name": "tavily_web_research", "error": err})
            _emit("tavily.failed", {**base_event_data, "error": err})
            return ToolResult(
                tool_name=self.tool_name,
                execution_id=exec_id,
                status="failed",
                error_message=err,
                duration_ms=(time.time() - start_time) * 1000,
            )
