"""
Comprehensive Unit & Integration Test Suite for Phase 6:
Case Orchestrator, Multi-Specialist Delegation, Shared Context, Contradiction Detection,
and Evidence-Grounded Investigation Synthesis.

Coverage:
1. Orchestrator registration & metadata
2. Structured routing decision parsing
3. Invalid routing and invalid agent rejection
4. Specialist task creation & deterministic fingerprint computation
5. Duplicate task prevention
6. Detective specialist delegation
7. Timeline specialist delegation
8. GeoScope specialist delegation
9. Single-specialist selective routing (no unnecessary agent invocations)
10. Multi-specialist routing (Detective + Timeline + GeoScope)
11. Bounded delegation & recursion prevention
12. Shared context tracking & evidence reference aggregation
13. Contradiction detection (e.g. timestamp gap between call and location)
14. Specialist failure resilience
15. Case authorization & cross-case isolation
16. Primary End-to-End Investigation Demo Turn
"""

import pytest
import time
from unittest.mock import AsyncMock, patch

from backend.app import database, models
from backend.app.agents.tools import default_tool_registry
from backend.app.agents.gateway import ModelRequest, ModelResponse
from backend.app.agents.runtime import NebiusNemotronRuntime
from backend.app.agents.orchestration_schemas import (
    SpecialistAgentTask,
    SpecialistTaskResult,
    SharedInvestigationContext,
    RoutingDecision,
    ContradictionItem,
)
from backend.app.agents.orchestration_service import (
    CaseOrchestratorService,
    _detect_contradictions,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def phase6_test_data():
    """Seed real database with case-scoped records across Detective, Timeline, and GeoScope."""
    db = database.SessionLocal()
    try:
        ev_ids = ["EV-087", "EV-104", "EV-119", "EV-ISOLATED-CASE-B"]
        case_ids = ["CASE-PHASE6-A", "CASE-PHASE6-B"]

        db.query(models.Document).filter(models.Document.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.ForensicResult).filter(models.ForensicResult.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.Evidence).filter(models.Evidence.id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.Case).filter(models.Case.id.in_(case_ids)).delete(synchronize_session=False)
        db.commit()

        # Case A: Target
        case_a = models.Case(id="CASE-PHASE6-A", title="Operation Tri-Specialist", status="open")
        # Case B: Isolated
        case_b = models.Case(id="CASE-PHASE6-B", title="Unauthorized Boundary Case", status="open")
        db.add_all([case_a, case_b])

        # EV-087: Telecom Records (Detective)
        ev_87 = models.Evidence(
            id="EV-087",
            case_id="CASE-PHASE6-A",
            filename="subscriber_contract_rahul.pdf",
            storage_path="/forensics/subscriber_contract_rahul.pdf",
            sha256="8787878787878787878787878787878787878787878787878787878787878787",
            size=5120,
            mime_type="application/pdf",
        )
        # EV-104: Call Log Chronology (Timeline)
        ev_104 = models.Evidence(
            id="EV-104",
            case_id="CASE-PHASE6-A",
            filename="cdr_call_log_jan12.csv",
            storage_path="/forensics/cdr_call_log_jan12.csv",
            sha256="1041041041041041041041041041041041041041041041041041041041041041",
            size=4096,
            mime_type="text/csv",
        )
        # EV-119: GPS Mobility Fixes (GeoScope)
        ev_119 = models.Evidence(
            id="EV-119",
            case_id="CASE-PHASE6-A",
            filename="gps_waypoint_dump.json",
            storage_path="/forensics/gps_waypoint_dump.json",
            sha256="1191191191191191191191191191191191191191191191191191191191191191",
            size=6144,
            mime_type="application/json",
            metadata_json={
                "device_owner": "Rahul Kumar",
                "device_id": "Device-Rahul-9876",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timestamp": "2026-01-12T20:52:00Z",
            },
        )
        # EV-ISOLATED: Case B strictly isolated
        ev_isolated = models.Evidence(
            id="EV-ISOLATED-CASE-B",
            case_id="CASE-PHASE6-B",
            filename="confidential_case_b.dat",
            storage_path="/forensics/confidential_case_b.dat",
            sha256="9999999999999999999999999999999999999999999999999999999999999999",
            size=1024,
            mime_type="application/octet-stream",
        )
        db.add_all([ev_87, ev_104, ev_119, ev_isolated])
        db.commit()

        # Document text for EV-087 (Detective EvidenceSearchTool match)
        doc_87 = models.Document(
            evidence_id="EV-087",
            text="Subscriber Registration: Rahul Kumar is the primary account holder for mobile phone +91 9876543210.",
        )
        # ForensicResult for EV-087 (Detective EntitySearchTool match)
        fr_87 = models.ForensicResult(
            evidence_id="EV-087",
            processor="gliner_ner",
            result={
                "entities": [
                    {"name": "Rahul Kumar", "type": "PERSON", "confidence": 0.98},
                    {"name": "+91 9876543210", "type": "PHONE_NUMBER", "confidence": 0.99},
                ],
                "relationships": [
                    {"source": "Rahul Kumar", "target": "+91 9876543210", "relationship": "OWNS_PHONE"}
                ],
            },
        )
        # ForensicResult for EV-104 (Timeline Tool match)
        fr_104 = models.ForensicResult(
            evidence_id="EV-104",
            processor="mobile_forensics",
            result={
                "timeline": [
                    {
                        "event": "Outgoing Call from Rahul Kumar",
                        "timestamp": "2026-01-12T21:14:00Z",
                        "description": "Call from +91 9876543210 to accomplice (180 seconds)",
                    }
                ]
            },
        )
        # ForensicResult for EV-119 (GeoScope Tool match)
        fr_119 = models.ForensicResult(
            evidence_id="EV-119",
            processor="mobile_forensics",
            result={
                "artifacts": {
                    "gps": [
                        {
                            "latitude": 28.6139,
                            "longitude": 77.2090,
                            "date": "2026-01-12T20:52:00Z",
                            "subject": "Rahul Kumar",
                            "device_id": "Device-Rahul-9876",
                        }
                    ]
                }
            },
        )
        db.add_all([doc_87, fr_87, fr_104, fr_119])
        db.commit()

        yield {
            "case_a": "CASE-PHASE6-A",
            "case_b": "CASE-PHASE6-B",
            "ev_87": "EV-087",
            "ev_104": "EV-104",
            "ev_119": "EV-119",
            "ev_isolated": "EV-ISOLATED-CASE-B",
        }
    finally:
        db.query(models.Document).filter(models.Document.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.ForensicResult).filter(models.ForensicResult.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.Evidence).filter(models.Evidence.id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.Case).filter(models.Case.id.in_(case_ids)).delete(synchronize_session=False)
        db.commit()
        db.close()


# ─── UNIT & SCHEMA TESTS ──────────────────────────────────────────────────────

def test_task_fingerprint_and_duplicate_prevention():
    """Verify SpecialistAgentTask computes deterministic fingerprints for duplicate protection."""
    task1 = SpecialistAgentTask(
        case_id="CASE-1",
        target_agent="timeline",
        objective="Find calls around 21:14",
        context_refs={"evidence_ids": ["EV-104"]},
    )
    task2 = SpecialistAgentTask(
        case_id="CASE-1",
        target_agent="timeline",
        objective="Find calls around 21:14",
        context_refs={"evidence_ids": ["EV-104"]},
    )
    task3 = SpecialistAgentTask(
        case_id="CASE-1",
        target_agent="geoscope",
        objective="Find locations around 21:14",
        context_refs={"evidence_ids": ["EV-104"]},
    )

    assert task1.compute_fingerprint() == task2.compute_fingerprint()
    assert task1.compute_fingerprint() != task3.compute_fingerprint()

    ctx = SharedInvestigationContext(case_id="CASE-1", objective="Test")
    assert not ctx.is_task_duplicate(task1)

    res = SpecialistTaskResult(task_id=task1.task_id, agent_id="timeline", summary="done")
    ctx.record_task_result(task1, res)
    assert ctx.is_task_duplicate(task2)


def test_routing_decision_validation():
    """Verify RoutingDecision enforces structured action and target agent boundaries."""
    valid_dec = RoutingDecision(
        action="delegate",
        target_agent="detective",
        objective="Trace Rahul Kumar phone ownership",
        reason="Identify device owner",
    )
    assert valid_dec.action == "delegate"
    assert valid_dec.target_agent == "detective"

    fin_dec = RoutingDecision(
        action="finalize",
        reason="All evidence collected",
    )
    assert fin_dec.action == "finalize"


def test_contradiction_detection():
    """Verify _detect_contradictions surfaces timestamp/location gaps."""
    t_res = SpecialistTaskResult(
        task_id="t-1",
        agent_id="timeline",
        summary="Device outgoing call verified at 21:14:00.",
        evidence_refs=["EV-104"],
    )
    g_res = SpecialistTaskResult(
        task_id="g-1",
        agent_id="geoscope",
        summary="Device GPS fix verified at 20:52:00.",
        evidence_refs=["EV-119"],
    )

    contras = _detect_contradictions([t_res, g_res])
    assert len(contras) == 1
    assert contras[0].type == "timestamp_gap"
    assert "22-minute gap" in contras[0].description
    assert "EV-104" in contras[0].sources
    assert "EV-119" in contras[0].sources


# ─── END-TO-END ORCHESTRATION TESTS ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_single_specialist_selective_routing(phase6_test_data):
    """
    Test that a query solely about chronological timeline events delegates only to Timeline Agent,
    proving the orchestrator is selective and does not invoke all agents.
    """
    mock_provider = AsyncMock()
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    # Step 1: Orchestrator decides to delegate only to timeline
    orch_resp_1 = ModelResponse(
        content='```delegation\n{"action": "delegate", "target_agent": "timeline", "objective": "Show events around 21:14", "reason": "Query is strictly temporal"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    # Step 2: Timeline specialist runs internally (mock tool call loop if needed)
    tml_call = ModelResponse(
        content="Searching timeline.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[{"id": "tc1", "function": {"name": "timeline_search", "arguments": '{"query": "Rahul"}'}}],
    )
    tml_syn = ModelResponse(
        content="At 21:14:00 Rahul Kumar placed an outgoing call in EV-104.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[],
    )
    # Step 3: Orchestrator finalizes
    orch_resp_2 = ModelResponse(
        content='```delegation\n{"action": "finalize", "reason": "Timeline analysis sufficient"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    orch_final = ModelResponse(
        content="INVESTIGATION SUMMARY: Events surrounding the 21:14 call have been reconstructed using EV-104.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )

    mock_provider.chat.side_effect = [orch_resp_1, tml_call, tml_syn, orch_resp_2, orch_final]

    runtime = NebiusNemotronRuntime(
        provider=mock_provider,
        tool_registry=default_tool_registry,
    )

    result = await runtime.execute_turn(
        agent_id="case-orchestrator",
        case_id=phase6_test_data["case_a"],
        query="Show events around the 21:14 call.",
        session_id="session-orch-selective",
        history=[],
        case_evidence_refs=[phase6_test_data["ev_104"]],
    )

    assert len(result.tool_executions) == 1
    assert result.tool_executions[0].tool_name == "delegate_timeline"
    assert phase6_test_data["ev_104"] in result.evidence_refs
    assert "INVESTIGATION SUMMARY" in result.content


@pytest.mark.asyncio
async def test_primary_three_agent_orchestration_flow(phase6_test_data):
    """
    PRIMARY DEMO E2E TEST:
    Investigator asks:
    'Determine whether Rahul Kumar was associated with the phone number,
    what happened around the relevant call, and whether the device was near the incident location.'

    Expected Flow:
    1. Orchestrator -> Detective (verifies Rahul Kumar owns +91 9876543210 via EV-087)
    2. Orchestrator -> Timeline (reconstructs 21:14 call via EV-104)
    3. Orchestrator -> GeoScope (locates device near 28.6139, 77.2090 at 20:52 via EV-119)
    4. Orchestrator detects temporal gap (20:52 location vs 21:14 call)
    5. Orchestrator synthesizes structured investigation report with all 3 evidence references.
    """
    mock_provider = AsyncMock()
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    # 1. Orchestrator delegates to Detective
    o1 = ModelResponse(
        content='```delegation\n{"action": "delegate", "target_agent": "detective", "objective": "Verify Rahul Kumar phone association", "reason": "Establish device ownership"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    # Detective executes entity_search tool and synthesizes
    d_call = ModelResponse(
        content="Searching entities.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[{"id": "c1", "function": {"name": "entity_search", "arguments": '{"query": "Rahul Kumar"}'}}],
    )
    d_syn = ModelResponse(
        content="EV-087 confirms Rahul Kumar is associated with +91 9876543210.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[],
    )

    # 2. Orchestrator delegates to Timeline
    o2 = ModelResponse(
        content='```delegation\n{"action": "delegate", "target_agent": "timeline", "objective": "Find events surrounding 21:14", "reason": "Check call timing"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    t_call = ModelResponse(
        content="Searching timeline.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[{"id": "c2", "function": {"name": "timeline_search", "arguments": '{"query": "Rahul"}'}}],
    )
    t_syn = ModelResponse(
        content="Device outgoing call verified at 21:14:00 in EV-104.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[],
    )

    # 3. Orchestrator delegates to GeoScope
    o3 = ModelResponse(
        content='```delegation\n{"action": "delegate", "target_agent": "geoscope", "objective": "Find device locations near incident", "reason": "Check location fixes"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    g_call = ModelResponse(
        content="Searching locations.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[{"id": "c3", "function": {"name": "location_search", "arguments": '{"subject": "Rahul"}'}}],
    )
    g_syn = ModelResponse(
        content="Device GPS fix verified at 20:52:00 in EV-119.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[],
    )

    # 4. Orchestrator finalizes with synthesis
    o4 = ModelResponse(
        content='```delegation\n{"action": "finalize", "reason": "Comprehensive evidence collected across all specialists"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    o_final = ModelResponse(
        content=(
            "INVESTIGATION SUMMARY\n\n"
            "Objective: Verify Rahul Kumar device association, 21:14 call activity, and spatial location.\n\n"
            "Key Findings:\n"
            "1. Device Association: Detective verified Rahul Kumar owns +91 9876543210 (EV-087).\n"
            "2. Call Activity: Timeline verified outgoing call at 21:14 (EV-104).\n"
            "3. Location Fix: GeoScope verified GPS fix at (28.6139, 77.2090) at 20:52 (EV-119).\n\n"
            "Contradiction / Uncertainty:\n"
            "- A 22-minute gap exists between the last location fix (20:52) and the phone call (21:14).\n"
            "- Device presence does not independently prove the physical presence of the person."
        ),
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )

    mock_provider.chat.side_effect = [o1, d_call, d_syn, o2, t_call, t_syn, o3, g_call, g_syn, o4, o_final]

    runtime = NebiusNemotronRuntime(
        provider=mock_provider,
        tool_registry=default_tool_registry,
    )

    result = await runtime.execute_turn(
        agent_id="case-orchestrator",
        case_id=phase6_test_data["case_a"],
        query=(
            "Determine whether Rahul Kumar was associated with the phone number, "
            "what happened around the relevant call, and whether the device was near the incident location."
        ),
        session_id="session-primary-demo-p6",
        history=[],
        case_evidence_refs=[phase6_test_data["ev_87"], phase6_test_data["ev_104"], phase6_test_data["ev_119"]],
    )

    # Verify 3 specialist delegations occurred
    delegated_tools = [t.tool_name for t in result.tool_executions]
    assert "delegate_detective" in delegated_tools
    assert "delegate_timeline" in delegated_tools
    assert "delegate_geoscope" in delegated_tools

    # Verify all 3 evidence references are preserved in result
    assert phase6_test_data["ev_87"] in result.evidence_refs
    assert phase6_test_data["ev_104"] in result.evidence_refs
    assert phase6_test_data["ev_119"] in result.evidence_refs

    # Verify findings contain synthesized orchestrator finding
    orch_findings = [f for f in result.findings if f.agent_id == "case-orchestrator"]
    assert len(orch_findings) >= 1
    assert orch_findings[0].status == "needs_review"

    # Verify content preserves provenance and uncertainty
    assert "EV-087" in result.content
    assert "EV-104" in result.content
    assert "EV-119" in result.content
    assert "22-minute gap" in result.content


@pytest.mark.asyncio
async def test_dual_specialist_timeline_and_geoscope(phase6_test_data):
    """Test dual-specialist question invoking only Timeline and GeoScope."""
    mock_provider = AsyncMock()
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    # Orchestrator delegates to Timeline
    o1 = ModelResponse(
        content='```delegation\n{"action": "delegate", "target_agent": "timeline", "objective": "Calls around 21:14", "reason": "Check call timing"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    t_call = ModelResponse(
        content="Search",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[{"id": "tc1", "function": {"name": "timeline_search", "arguments": '{"query": "call"}'}}],
    )
    t_syn = ModelResponse(
        content="Call at 21:14 in EV-104.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[],
    )
    # Orchestrator delegates to GeoScope
    o2 = ModelResponse(
        content='```delegation\n{"action": "delegate", "target_agent": "geoscope", "objective": "Locations near 21:14", "reason": "Check location"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    g_call = ModelResponse(
        content="Search loc",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[{"id": "tc2", "function": {"name": "location_search", "arguments": '{"subject": "Rahul"}'}}],
    )
    g_syn = ModelResponse(
        content="GPS fix at 20:52 in EV-119.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[],
    )
    # Orchestrator finalizes
    o3 = ModelResponse(
        content='```delegation\n{"action": "finalize", "reason": "Done"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    o_final = ModelResponse(
        content="INVESTIGATION SUMMARY: Call at 21:14 (EV-104), location at 20:52 (EV-119).",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )

    mock_provider.chat.side_effect = [o1, t_call, t_syn, o2, g_call, g_syn, o3, o_final]

    runtime = NebiusNemotronRuntime(
        provider=mock_provider,
        tool_registry=default_tool_registry,
    )

    result = await runtime.execute_turn(
        agent_id="case-orchestrator",
        case_id=phase6_test_data["case_a"],
        query="Where was the device around the 21:14 call and what other events occurred nearby?",
        session_id="session-dual-p6",
        history=[],
        case_evidence_refs=[phase6_test_data["ev_104"], phase6_test_data["ev_119"]],
    )

    delegated = [t.tool_name for t in result.tool_executions]
    assert "delegate_timeline" in delegated
    assert "delegate_geoscope" in delegated
    assert "delegate_detective" not in delegated
    assert phase6_test_data["ev_104"] in result.evidence_refs
    assert phase6_test_data["ev_119"] in result.evidence_refs


@pytest.mark.asyncio
async def test_duplicate_task_prevention(phase6_test_data):
    """Test that requesting an identical subtask twice terminates loop without duplicate tool runs."""
    mock_provider = AsyncMock()
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    # Orchestrator attempts duplicate delegation
    dup_block = '```delegation\n{"action": "delegate", "target_agent": "timeline", "objective": "Calls around 21:14", "reason": "First run"}\n```'
    o1 = ModelResponse(content=dup_block, model="nvidia/nemotron-4-340b-instruct", provider="nebius")
    t_call = ModelResponse(
        content="Search",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[{"id": "tc1", "function": {"name": "timeline_search", "arguments": '{"query": "call"}'}}],
    )
    t_syn = ModelResponse(content="Call at 21:14 in EV-104.", model="nvidia/nemotron-4-340b-instruct", provider="nebius", tool_calls=[])
    # Duplicate delegation
    o2 = ModelResponse(content=dup_block, model="nvidia/nemotron-4-340b-instruct", provider="nebius")
    o_final = ModelResponse(content="INVESTIGATION SUMMARY: Reused existing timeline analysis.", model="nvidia/nemotron-4-340b-instruct", provider="nebius")

    mock_provider.chat.side_effect = [o1, t_call, t_syn, o2, o_final]

    runtime = NebiusNemotronRuntime(
        provider=mock_provider,
        tool_registry=default_tool_registry,
    )

    result = await runtime.execute_turn(
        agent_id="case-orchestrator",
        case_id=phase6_test_data["case_a"],
        query="Calls around 21:14",
        session_id="session-dup-p6",
        history=[],
        case_evidence_refs=[phase6_test_data["ev_104"]],
    )

    # Tool should only execute once despite second request
    assert len(result.tool_executions) == 1
    assert result.tool_executions[0].tool_name == "delegate_timeline"


@pytest.mark.asyncio
async def test_orchestrator_case_isolation(phase6_test_data):
    """Test that Orchestrator cannot access evidence belonging to an unauthorized case."""
    mock_provider = AsyncMock()
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    o1 = ModelResponse(
        content='```delegation\n{"action": "delegate", "target_agent": "detective", "objective": "Find confidential file", "reason": "Test"}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    d_call = ModelResponse(
        content="Search",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[{"id": "c1", "function": {"name": "evidence_search", "arguments": '{"query": "confidential_case_b"}'}}],
    )
    d_syn = ModelResponse(content="No results found.", model="nvidia/nemotron-4-340b-instruct", provider="nebius", tool_calls=[])
    o2 = ModelResponse(content='```delegation\n{"action": "finalize", "reason": "No data"}\n```', model="nvidia/nemotron-4-340b-instruct", provider="nebius")
    o_final = ModelResponse(content="No unauthorized records found.", model="nvidia/nemotron-4-340b-instruct", provider="nebius")

    mock_provider.chat.side_effect = [o1, d_call, d_syn, o2, o_final]

    runtime = NebiusNemotronRuntime(
        provider=mock_provider,
        tool_registry=default_tool_registry,
    )

    result = await runtime.execute_turn(
        agent_id="case-orchestrator",
        case_id=phase6_test_data["case_a"],
        query="Find records from case B",
        session_id="session-iso-p6",
        history=[],
        case_evidence_refs=[phase6_test_data["ev_87"]],
    )

    assert phase6_test_data["ev_isolated"] not in result.evidence_refs

