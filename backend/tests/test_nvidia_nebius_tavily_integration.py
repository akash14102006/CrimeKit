"""
Integration tests for CrimeKit Phase 12B/C:
- Nebius Token Factory & NVIDIA Nemotron Provider
- Tavily Web Research Tool & Provenance
- NemoClaw & OpenShell Security Sandbox
- NeMo Agent Toolkit Adapter
- Speech NIM Audio Forensics
- Provider Health & Telemetry
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from backend.app.tools.tavily_tool import TavilyWebResearchTool
from backend.app.security.agent_sandbox import sandbox, SandboxPolicyViolation, APPROVED_TOOLS
from backend.app.agents.nat_adapter import nat_adapter
from backend.app.forensics.speech_nim import speech_nim


def test_approved_tool_registry():
    """Verify NemoClaw / OpenShell default-deny approved tool set."""
    assert "evidence_search" in APPROVED_TOOLS
    assert "tavily_web_research" in APPROVED_TOOLS
    assert "location_search" in APPROVED_TOOLS
    assert "rm_rf" not in APPROVED_TOOLS
    assert "arbitrary_shell" not in APPROVED_TOOLS


def test_nemoclaw_sandbox_policy_enforcement():
    """Verify sandbox allows permitted tools and denies unauthorized/out-of-scope calls."""
    case_id = "CASE-2026-001"

    # Permitted tool for detective
    assert sandbox.validate_tool_execution(
        agent_id="detective",
        tool_name="evidence_search",
        case_id=case_id,
        arguments={"case_id": case_id, "query": "Rahul"},
    ) is True

    # Permitted Tavily tool for detective
    assert sandbox.validate_tool_execution(
        agent_id="detective",
        tool_name="tavily_web_research",
        case_id=case_id,
        arguments={"case_id": case_id, "query": "Acme Corp"},
    ) is True

    # Denied tool out of scope (Timeline calling location_search directly)
    with pytest.raises(SandboxPolicyViolation) as exc:
        sandbox.validate_tool_execution(
            agent_id="timeline",
            tool_name="location_search",
            case_id=case_id,
            arguments={"case_id": case_id},
        )
    assert "not authorized" in exc.value.message

    # Denied cross-case leak attempt
    with pytest.raises(SandboxPolicyViolation) as exc_leak:
        sandbox.validate_tool_execution(
            agent_id="detective",
            tool_name="evidence_search",
            case_id=case_id,
            arguments={"case_id": "CASE-LEAK-OTHER-CASE"},
        )
    assert "Cross-case access" in exc_leak.value.message


@pytest.mark.asyncio
async def test_tavily_web_research_tool():
    """Verify Tavily web research stamps results as EXTERNAL WEB SOURCE."""
    tool = TavilyWebResearchTool()
    res = await tool.execute(
        case_id="CASE-2026-001",
        user_id="inv-001",
        arguments={"query": "Telecom Spectrum Provider", "max_results": 2},
        context={"agent": "detective", "session_id": "sess-test-01"},
    )
    assert res.status == "completed"
    assert res.result_count > 0
    results = res.results
    assert len(results) > 0
    assert results[0]["source"] == "tavily"
    assert results[0]["provenance"] == "EXTERNAL WEB SOURCE"
    assert results[0]["is_primary_evidence"] is False
    assert results[0]["agent"] == "detective"
    assert results[0]["case_id"] == "CASE-2026-001"
    assert "url" in results[0]
    assert "retrieved_at" in results[0]


@pytest.mark.asyncio
async def test_tavily_agent_permissions_isolation():
    """Verify Tavily is allowed for Detective, GeoScope, Testimony, Orchestrator and blocked for Timeline and Report."""
    from backend.app.agents.tools import default_tool_registry

    for allowed_agent in ["detective", "geoscope", "testimony", "case-orchestrator"]:
        res = await default_tool_registry.execute(
            "tavily_web_research",
            case_id="CASE-2026-001",
            user_id="test-user",
            arguments={"query": "Rahul Kumar corporate telecommunications India"},
            context={"agent": allowed_agent},
        )
        assert res.status == "completed"

    for blocked_agent in ["timeline", "report"]:
        res = await default_tool_registry.execute(
            "tavily_web_research",
            case_id="CASE-2026-001",
            user_id="test-user",
            arguments={"query": "Rahul Kumar corporate telecommunications India"},
            context={"agent": blocked_agent},
        )
        assert res.status == "failed"
        assert "not authorized" in res.error_message


@pytest.mark.asyncio
async def test_tavily_case_isolation_enforcement():
    """Verify cross-case access is blocked when attempting to override case_id in Tavily query."""
    from backend.app.agents.tools import default_tool_registry
    res = await default_tool_registry.execute(
        "tavily_web_research",
        case_id="CASE-2026-001",
        user_id="test-user",
        arguments={"query": "Rahul Kumar", "case_id": "CASE-OTHER"},
        context={"agent": "detective"},
    )
    assert res.status == "failed"
    assert "Cross-case access attempt" in res.error_message



def test_nat_workflow_tracing_adapter():
    """Verify NeMo Agent Toolkit adapter captures workflow spans and metrics."""
    span_id = nat_adapter.start_workflow_span(
        name="detective_lead_correlation",
        agent_id="detective",
        case_id="CASE-2026-001",
        session_id="sess-nat-1",
    )
    assert span_id.startswith("nat_")

    finished = nat_adapter.finish_workflow_span(span_id, status="completed")
    assert finished is not None
    assert finished.status == "completed"
    assert finished.duration_ms >= 0.0

    summary = nat_adapter.get_metrics_summary("CASE-2026-001")
    assert summary["toolkit"] == "NVIDIA NeMo Agent Toolkit"
    assert summary["total_workflow_spans"] >= 1


@pytest.mark.asyncio
async def test_nat_tool_bridge_execution_and_isolation():
    """Verify NAT tool bridge dispatches all Detective tools and strictly enforces case boundaries."""
    case_id = "CASE-2026-001"

    # Bridge tool definitions
    tool_defs = nat_adapter.get_tool_definitions("detective")
    names = [t["name"] for t in tool_defs]
    assert "evidence_search" in names
    assert "entity_search" in names
    assert "knowledge_graph_traversal" in names
    assert "vector_search" in names

    # Authorized executions
    r1 = await nat_adapter.execute_tool_bridge("evidence_search", case_id=case_id, arguments={"query": "Rahul"}, agent_id="detective")
    assert r1.status == "completed"

    r2 = await nat_adapter.execute_tool_bridge("entity_search", case_id=case_id, arguments={"query": "Rahul"}, agent_id="detective")
    assert r2.status == "completed"

    r3 = await nat_adapter.execute_tool_bridge("knowledge_graph_query", case_id=case_id, arguments={"entity": "Rahul"}, agent_id="detective")
    assert r3.status == "completed"

    r4 = await nat_adapter.execute_tool_bridge("vector_search", case_id=case_id, arguments={"query": "Rahul"}, agent_id="detective")
    assert r4.status == "completed"

    # Case isolation override blocked
    r_iso = await nat_adapter.execute_tool_bridge("evidence_search", case_id=case_id, arguments={"query": "Rahul", "case_id": "CASE-OTHER"}, agent_id="detective")
    assert r_iso.status == "failed"
    assert "Cross-case access attempt" in r_iso.error_message

    # Unauthorized tool blocked
    r_perm = await nat_adapter.execute_tool_bridge("movement_trace", case_id=case_id, arguments={"entity": "Rahul"}, agent_id="detective")
    assert r_perm.status == "failed"
    assert "not authorized" in r_perm.error_message


@pytest.mark.asyncio
async def test_speech_nim_audio_forensics():
    """Verify Speech NIM transcription produces timestamped segments."""
    result = await speech_nim.transcribe_audio_evidence(
        evidence_id="EV-AUDIO-99",
        case_id="CASE-2026-001",
    )
    assert result.evidence_id == "EV-AUDIO-99"
    assert len(result.timestamps) > 0
    assert "Rahul" in result.transcript
    assert result.confidence >= 0.9

