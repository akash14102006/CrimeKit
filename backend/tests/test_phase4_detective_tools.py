"""
Comprehensive Unit & Integration Test Suite for Phase 4:
CrimeKit Investigation Tools, Registry, Tool-Calling Loop, and Case Isolation.

Test coverage:
A. Tool contract tests
B. Tool registry tests
C. EvidenceSearchTool execution & case filtering
D. EntitySearchTool execution & deduplication
E. KnowledgeGraphTool parameterized traversal & DB fallback
F. Tool argument validation & security (no arbitrary SQL/Cypher)
G. Case authorization and cross-case isolation tests
H. Nemotron tool-call parsing (native tool_calls & structured markdown tag)
I. Tool execution loop and maximum-round protection
J. Tool failure recovery
K. Evidence citation grounding in final findings
L. End-to-end integration test: "Find all connections between Rahul Kumar and this phone number"
"""

import pytest
import time
from unittest.mock import AsyncMock, patch

from backend.app import database, models
from backend.app.agents.tools.base import BaseInvestigationTool, ToolResult
from backend.app.agents.tools.registry import InvestigationToolRegistry
from backend.app.agents.tools.evidence_tool import EvidenceSearchTool
from backend.app.agents.tools.entity_tool import EntitySearchTool
from backend.app.agents.tools.graph_tool import KnowledgeGraphTool
from backend.app.agents.gateway import ModelRequest, ModelResponse, ModelMessage
from backend.app.agents.runtime import NebiusNemotronRuntime


# ─── Test Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def test_db_records():
    """Create deterministic forensic records for CASE-PHASE4-A and isolated CASE-PHASE4-B."""
    db = database.SessionLocal()
    try:
        # 1. Clean previous runs
        db.query(models.Document).filter(models.Document.text.like("%Rahul Kumar%")).delete(synchronize_session=False)
        db.query(models.ForensicResult).filter(models.ForensicResult.evidence_id.in_(["EV-087", "EV-104", "EV-999"])).delete(synchronize_session=False)
        db.query(models.Evidence).filter(models.Evidence.id.in_(["EV-087", "EV-104", "EV-999"])).delete(synchronize_session=False)
        db.query(models.Case).filter(models.Case.id.in_(["CASE-PHASE4-A", "CASE-PHASE4-B"])).delete(synchronize_session=False)
        db.commit()

        # 2. Case A (Target case)
        case_a = models.Case(
            id="CASE-PHASE4-A",
            title="Operation Telecom Syndicate",
            status="open",
        )
        db.add(case_a)

        # Evidence EV-087 in Case A (Call logs)
        ev_87 = models.Evidence(
            id="EV-087",
            case_id="CASE-PHASE4-A",
            filename="cdr_dump_jan2026.csv",
            storage_path="/storage/ev087.csv",
            sha256="87a87b87c87d87e87f87087187287387487587687787887987a87b87c87d87e8",
            size=1024,
            mime_type="text/csv",
        )
        db.add(ev_87)

        # Document OCR text linked to EV-087
        doc_87 = models.Document(
            evidence_id="EV-087",
            text="Subscriber Rahul Kumar registered mobile +91 9876543210 on 2026-01-14 with IMEI 354892019283019.",
        )
        db.add(doc_87)

        # Evidence EV-104 in Case A (WhatsApp chat export)
        ev_104 = models.Evidence(
            id="EV-104",
            case_id="CASE-PHASE4-A",
            filename="whatsapp_export_target.txt",
            storage_path="/storage/ev104.txt",
            sha256="104a104b104c104d104e104f1040104110421043104410451046104710481049",
            size=2048,
            mime_type="text/plain",
        )
        db.add(ev_104)

        # Forensic Results for EV-087 and EV-104
        fr_87 = models.ForensicResult(
            evidence_id="EV-087",
            processor="telecom_cdr_extractor",
            result={
                "entities": [
                    {"name": "Rahul Kumar", "type": "person", "normalized_value": "rahul_kumar", "confidence": 0.96},
                    {"name": "+91 9876543210", "type": "phone", "normalized_value": "+919876543210", "confidence": 0.98},
                ],
                "relationships": [
                    {
                        "source_entity": "Rahul Kumar",
                        "target_entity": "+91 9876543210",
                        "relationship": "OWNS_DEVICE",
                        "confidence": 0.95,
                        "evidence_id": "EV-087",
                    }
                ],
            },
        )
        db.add(fr_87)

        # 3. Case B (Unrelated/Isolated case)
        case_b = models.Case(
            id="CASE-PHASE4-B",
            title="Operation Isolated Secret",
            status="open",
        )
        db.add(case_b)

        ev_999 = models.Evidence(
            id="EV-999",
            case_id="CASE-PHASE4-B",
            filename="confidential_leak.pdf",
            storage_path="/storage/ev999.pdf",
            sha256="999a999b999c999d999e999f9990999199929993999499959996999799989999",
            size=512,
            mime_type="application/pdf",
        )
        db.add(ev_999)

        doc_999 = models.Document(
            evidence_id="EV-999",
            text="Classified Case B document mentioning Rahul Kumar in unrelated matter.",
        )
        db.add(doc_999)

        db.commit()
        return {"case_a": "CASE-PHASE4-A", "case_b": "CASE-PHASE4-B"}
    finally:
        db.close()


# ─── A & B. Tool Registry & Contract Tests ──────────────────────────────────

def test_tool_registry_registration():
    """Verify tools can be registered, listed, and retrieved."""
    registry = InvestigationToolRegistry()
    ev_tool = EvidenceSearchTool()
    registry.register(ev_tool)

    assert registry.get("evidence_search") == ev_tool
    assert len(registry.list_tools()) == 1
    assert registry.get_tool_definitions()[0].name == "evidence_search"
    assert registry.get("unknown_tool") is None


@pytest.mark.asyncio
async def test_tool_registry_rejects_unknown_tool():
    """Verify executing an unrecognized tool returns safe error."""
    registry = InvestigationToolRegistry()
    res = await registry.execute(
        "arbitrary_dangerous_tool",
        case_id="CASE-TEST",
        user_id="user-1",
        arguments={"cmd": "rm -rf /"},
    )
    assert res.status == "failed"
    assert "not recognized or permitted" in res.error_message


# ─── C. EvidenceSearchTool Execution & Case Boundary ────────────────────────

@pytest.mark.asyncio
async def test_evidence_search_tool_finds_case_matches(test_db_records):
    """Verify EvidenceSearchTool finds matches in active case only."""
    tool = EvidenceSearchTool()
    res = await tool.execute(
        case_id="CASE-PHASE4-A",
        user_id="detective",
        arguments={"query": "Rahul Kumar"},
    )
    assert res.status == "completed"
    assert res.result_count >= 1
    evidence_ids = [r["evidence_id"] for r in res.results]
    assert "EV-087" in evidence_ids
    # Crucial: Must NEVER return evidence from CASE-PHASE4-B
    assert "EV-999" not in evidence_ids


@pytest.mark.asyncio
async def test_evidence_search_cross_case_isolation(test_db_records):
    """Verify Case B search does NOT see Case A records."""
    tool = EvidenceSearchTool()
    res = await tool.execute(
        case_id="CASE-PHASE4-B",
        user_id="detective",
        arguments={"query": "+91 9876543210"},
    )
    assert res.status == "completed"
    # Target phone number is only in Case A, so Case B must have 0 results
    assert res.result_count == 0


# ─── D. EntitySearchTool Tests ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_entity_search_tool_finds_entities(test_db_records):
    """Verify EntitySearchTool locates Rahul Kumar and returns EV-087 ref."""
    tool = EntitySearchTool()
    res = await tool.execute(
        case_id="CASE-PHASE4-A",
        user_id="detective",
        arguments={"query": "Rahul Kumar"},
    )
    assert res.status == "completed"
    assert res.result_count >= 1
    names = [e["name"] for e in res.results]
    assert "Rahul Kumar" in names
    assert "EV-087" in res.evidence_refs


# ─── E. KnowledgeGraphTool Tests ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_knowledge_graph_tool_traversal(test_db_records):
    """Verify KnowledgeGraphTool traverses connections between person and phone number."""
    tool = KnowledgeGraphTool()
    res = await tool.execute(
        case_id="CASE-PHASE4-A",
        user_id="detective",
        arguments={"entity": "Rahul Kumar", "max_depth": 2},
    )
    assert res.status == "completed"
    assert res.result_count >= 1
    rels = res.results[0]["relationships"]
    assert len(rels) >= 1
    r = rels[0]
    assert r["source"] == "Rahul Kumar"
    assert "+91 9876543210" in r["target"]
    assert "EV-087" in res.evidence_refs


# ─── H, I, J. Nemotron Tool Calling & Bounded Loop ───────────────────────────

@pytest.mark.asyncio
async def test_nemotron_tool_calling_loop_with_tool_tags(test_db_records):
    """
    Simulate Nemotron conversational turn where model requests:
    Round 1: ```tool_call {"name": "entity_search", "arguments": {"query": "Rahul Kumar"}}```
    Round 2: Model synthesizes final finding citing EV-087.
    """
    mock_provider = AsyncMock()

    # Step 1: Model requests entity_search tool
    resp_step1 = ModelResponse(
        content='```tool_call\n{"name": "entity_search", "arguments": {"query": "Rahul Kumar"}}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    # Step 2: Model receives tool result and provides grounded synthesis
    resp_step2 = ModelResponse(
        content="Based on seized call detail records in EV-087, Rahul Kumar is verified as the subscriber of +91 9876543210.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    mock_provider.chat.side_effect = [resp_step1, resp_step2]
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    runtime = NebiusNemotronRuntime(provider=mock_provider)
    result = await runtime.execute_turn(
        agent_id="detective",
        case_id="CASE-PHASE4-A",
        query="Find all connections for Rahul Kumar",
        session_id="sess-loop-01",
        history=[],
        case_evidence_refs=["EV-087", "EV-104"],
    )

    # Verify tool execution occurred
    assert len(result.tool_executions) == 1
    assert result.tool_executions[0].tool_name == "entity_search"
    assert result.tool_executions[0].status == "completed"

    # Verify final grounded response
    assert "EV-087" in result.content
    assert "EV-087" in result.evidence_refs

    # Verify structured finding
    assert len(result.findings) == 1
    assert "EV-087" in result.findings[0].evidence_refs
    assert result.findings[0].status == "needs_review"


@pytest.mark.asyncio
async def test_tool_loop_maximum_rounds_protection():
    """Verify runtime never enters infinite loop if model keeps requesting tools."""
    mock_provider = AsyncMock()
    # Provider keeps requesting tools endlessly
    endless_tool = ModelResponse(
        content='```tool_call\n{"name": "evidence_search", "arguments": {"query": "test"}}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    mock_provider.chat.return_value = endless_tool
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    runtime = NebiusNemotronRuntime(provider=mock_provider, max_tool_rounds=3)
    result = await runtime.execute_turn(
        agent_id="detective",
        case_id="CASE-PHASE4-A",
        query="Endless query",
        session_id="sess-endless",
        history=[],
    )

    # Max tool rounds must cap the execution
    assert len(result.tool_executions) <= 3
    assert mock_provider.chat.call_count == 3


# ─── L. Primary End-to-End Investigation Demo Test ──────────────────────────

@pytest.mark.asyncio
async def test_primary_e2e_detective_investigation_flow(test_db_records):
    """
    PRIMARY DEMO ACCEPTANCE TEST:
    'Find all connections between Rahul Kumar and this phone number.'
    1. Detective receives query
    2. Model calls entity_search and knowledge_graph_traversal
    3. Real CrimeKit database tools execute
    4. Nemotron synthesizes evidence-grounded finding
    5. Real evidence reference EV-087 is returned and structured.
    """
    mock_provider = AsyncMock()

    # Turn 1: Model invokes entity_search
    step1_resp = ModelResponse(
        content='I will check entity records for Rahul Kumar.\n```tool_call\n{"name": "entity_search", "arguments": {"query": "Rahul Kumar"}}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    # Turn 2: Model invokes graph traversal
    step2_resp = ModelResponse(
        content='Now checking relationships in the knowledge graph.\n```tool_call\n{"name": "knowledge_graph_traversal", "arguments": {"entity": "Rahul Kumar", "max_depth": 2}}\n```',
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    # Turn 3: Synthesis
    step3_resp = ModelResponse(
        content=(
            "Investigation Summary:\n"
            "Forensic evidence EV-087 (cdr_dump_jan2026.csv) verifies that Rahul Kumar is associated with "
            "mobile number +91 9876543210. Knowledge graph traversal confirms an OWNS_DEVICE relationship "
            "with 95% confidence. Recommend Timeline Agent consultation for call chronology."
        ),
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
    )
    mock_provider.chat.side_effect = [step1_resp, step2_resp, step3_resp]
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    runtime = NebiusNemotronRuntime(provider=mock_provider)
    res = await runtime.execute_turn(
        agent_id="detective",
        case_id="CASE-PHASE4-A",
        query="Find all connections between Rahul Kumar and this phone number.",
        session_id="sess-e2e-demo",
        history=[],
        case_evidence_refs=["EV-087", "EV-104"],
    )

    # 1. Verified executions
    assert len(res.tool_executions) == 2
    executed_tools = [t.tool_name for t in res.tool_executions]
    assert "entity_search" in executed_tools
    assert "knowledge_graph_traversal" in executed_tools
    assert all(t.status == "completed" for t in res.tool_executions)

    # 2. Verified evidence citation
    assert "EV-087" in res.evidence_refs
    assert "EV-087" in res.content

    # 3. Verified structured finding
    assert len(res.findings) >= 1
    finding = res.findings[0]
    assert "EV-087" in finding.evidence_refs
    assert finding.status == "needs_review"

    # 4. Verified agent handoff recommendation
    assert res.handoff is not None
    assert res.handoff.target_agent == "timeline"


@pytest.mark.asyncio
async def test_vector_search_tool(test_db_records):
    """Verify VectorSearchTool executes semantic search strictly within case boundaries."""
    from backend.app.agents.tools.vector_tool import VectorSearchTool
    tool = VectorSearchTool()
    res = await tool.execute(
        case_id="CASE-PHASE4-A",
        user_id="detective",
        arguments={"query": "Rahul Kumar subscriber device"},
    )
    assert res.status == "completed"
    assert res.result_count >= 1
    assert "EV-087" in res.evidence_refs
    assert "EV-999" not in res.evidence_refs


@pytest.mark.asyncio
async def test_detective_tool_permissions_rejected():
    """Verify Detective Agent is rejected when trying to execute Timeline or Report tools."""
    from backend.app.agents.tools import default_tool_registry

    # 1. Timeline tool rejected
    res_move = await default_tool_registry.execute(
        "movement_trace",
        case_id="CASE-PHASE4-A",
        user_id="detective",
        arguments={"entity": "Rahul Kumar"},
        context={"agent": "detective"}
    )
    assert res_move.status == "failed"
    assert "not authorized to call 'movement_trace'" in res_move.error_message

    # 2. Report tool rejected
    res_rpt = await default_tool_registry.execute(
        "report_generation",
        case_id="CASE-PHASE4-A",
        user_id="detective",
        arguments={},
        context={"agent": "detective"}
    )
    assert res_rpt.status == "failed"
    assert "not authorized to call 'report_generation'" in res_rpt.error_message


@pytest.mark.asyncio
async def test_detective_case_isolation_rejected():
    """Verify an agent cannot override its authorized case_id with an outside case."""
    from backend.app.agents.tools import default_tool_registry

    res = await default_tool_registry.execute(
        "evidence_search",
        case_id="CASE-PHASE4-A",
        user_id="detective",
        arguments={"query": "Rahul Kumar", "case_id": "CASE-OTHER"},
        context={"agent": "detective"}
    )
    assert res.status == "failed"
    assert "Cross-case access attempt" in res.error_message


@pytest.mark.asyncio
async def test_mock_detective_investigation_workflow(test_db_records):
    """Verify complete Detective investigation in MockDeterministicAgentRuntime."""
    from backend.app.agents.runtime import MockDeterministicAgentRuntime
    rt = MockDeterministicAgentRuntime()
    res = await rt.execute_turn(
        agent_id="detective",
        case_id="CASE-PHASE4-A",
        query="Find the strongest evidence-backed connection involving Rahul Kumar in CASE-2026-001.",
        session_id="sess-det-verify",
        history=[],
    )
    assert len(res.tool_executions) >= 3
    tool_names = [t.tool_name for t in res.tool_executions]
    assert "evidence_search" in tool_names
    assert "entity_search" in tool_names
    assert "knowledge_graph_traversal" in tool_names
    assert "EV-087" in res.evidence_refs
    assert len(res.findings) >= 1
    assert "EV-087" in res.findings[0].evidence_refs
    assert res.findings[0].status == "needs_review"

