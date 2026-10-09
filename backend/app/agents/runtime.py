"""
Agent Runtime Abstraction & Deterministic/Mock Runtime Layer.

Provides clean pluggable AgentRuntime interface for Phase 2.
In Phase 3+, this will be substituted by NebiusNemotronRuntime without
modifying API routes, session persistence, or frontend contracts.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import time
import uuid

from .schemas import (
    ToolExecutionContract,
    FindingContract,
    AgentHandoffContract,
)
from .metadata import CANONICAL_AGENTS


class AgentRuntimeResult:
    def __init__(
        self,
        content: str,
        tool_executions: List[ToolExecutionContract],
        findings: List[FindingContract],
        evidence_refs: List[str],
        confidence: Optional[float] = None,
        handoff: Optional[AgentHandoffContract] = None,
    ):
        self.content = content
        self.tool_executions = tool_executions
        self.findings = findings
        self.evidence_refs = evidence_refs
        self.confidence = confidence
        self.handoff = handoff


class BaseAgentRuntime(ABC):
    """Abstract interface defining the execution contract of an agent."""

    @abstractmethod
    async def execute_turn(
        self,
        agent_id: str,
        case_id: str,
        query: str,
        session_id: str,
        history: List[Dict[str, Any]],
        case_evidence_refs: Optional[List[str]] = None,
    ) -> AgentRuntimeResult:
        """Process a conversational turn for the specialist agent."""
        pass


class MockDeterministicAgentRuntime(BaseAgentRuntime):
    """
    Deterministic Agent Runtime for Phase 2 architectural verification.
    Produces agent-specific structured results, tool execution sequences,
    forensic findings marked as DEMO DATA, and handoff recommendations.
    """

    async def execute_turn(
        self,
        agent_id: str,
        case_id: str,
        query: str,
        session_id: str,
        history: List[Dict[str, Any]],
        case_evidence_refs: Optional[List[str]] = None,
    ) -> AgentRuntimeResult:
        now = time.time()
        agent_meta = CANONICAL_AGENTS.get(agent_id)
        agent_name = agent_meta.name if agent_meta else "Specialist Agent"
        ev_refs = case_evidence_refs if case_evidence_refs else ["EV-087", "EV-104"]

        # ── 1. Case Orchestrator ──
        if agent_id == "case-orchestrator":
            tools = [
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="case_audit",
                    display_name="Auditing Case Evidence Index",
                    status="completed",
                    started_at=now,
                    completed_at=now + 0.1,
                    output_snippet="Audited 12 evidence records, 3 active hypotheses.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="multi_agent_router",
                    display_name="Routing Investigation Subtasks",
                    status="completed",
                    started_at=now + 0.1,
                    completed_at=now + 0.2,
                    output_snippet="Dispatched entity correlation subtask to Detective Agent.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="synthesis_engine",
                    display_name="Synthesizing Cross-Domain Leads",
                    status="completed",
                    started_at=now + 0.2,
                    completed_at=now + 0.3,
                    output_snippet="Detected temporal overlap between suspect call logs and warehouse presence.",
                ),
            ]
            findings = [
                FindingContract(
                    id=f"find-{uuid.uuid4().hex[:6]}",
                    title="Coordinated Evidence Correlation Required [DEMO DATA]",
                    description="Multiple unlinked artifacts require relationship traversal and chronological alignment.",
                    confidence=0.88,
                    status="needs_review",
                    agent_id="case-orchestrator",
                    evidence_refs=ev_refs[:2],
                )
            ]
            handoff = AgentHandoffContract(
                source_agent="case-orchestrator",
                target_agent="detective",
                reason="Discovered unlinked communication identifiers requiring deep entity correlation.",
                context_summary="Investigate links between primary suspect and extracted phone numbers.",
            )
            content = (
                f"[Phase 2 Backend Architecture]\n\n"
                f"As {agent_name}, I evaluated case {case_id} for the query: '{query}'. "
                f"I reviewed the case index and orchestrated forensic leads. "
                f"I recommend delegating the deep entity traversal to Detective Agent."
            )
            return AgentRuntimeResult(content, tools, findings, ev_refs[:2], 0.88, handoff)

        # ── 2. Detective Agent ──
        elif agent_id == "detective":
            from .tools import default_tool_registry
            tools: List[ToolExecutionContract] = []
            collected_evidence_refs: List[str] = []
            detected_connection = None

            from .nat_adapter import nat_adapter

            # Helper to run and log a registered tool via NAT adapter workflow bridge
            async def _run_tool(t_name: str, args: Dict[str, Any], display: str):
                t_start = time.time()
                tres = await nat_adapter.execute_tool_bridge(
                    tool_name=t_name,
                    case_id=case_id,
                    user_id=f"{agent_id}-agent",
                    arguments=args,
                    agent_id=agent_id,
                    session_id=session_id,
                )
                t_end = time.time()
                for ref in tres.evidence_refs:
                    if ref and ref not in collected_evidence_refs:
                        collected_evidence_refs.append(ref)
                
                snippet = f"Returned {tres.result_count} items."
                if tres.results and isinstance(tres.results[0], dict):
                    if t_name == "evidence_search" and "snippet" in tres.results[0]:
                        snippet = tres.results[0]["snippet"][:120]
                    elif t_name == "entity_search" and "name" in tres.results[0]:
                        snippet = f"Found entity: {tres.results[0]['name']} ({tres.results[0].get('entity_type', 'entity')})"
                    elif t_name in ("knowledge_graph_traversal", "knowledge_graph_query") and "relationships" in tres.results[0]:
                        rels = tres.results[0]["relationships"]
                        if rels:
                            r0 = rels[0]
                            snippet = f"Connection: {r0.get('source')} -[{r0.get('relationship')}]-> {r0.get('target')}"
                    elif t_name == "vector_search" and "snippet" in tres.results[0]:
                        snippet = f"Semantic match: {tres.results[0]['snippet'][:100]}"

                contract = ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name=t_name,
                    display_name=display,
                    status=tres.status if tres.status != "permission_denied" else "failed",
                    started_at=t_start,
                    completed_at=t_end,
                    output_snippet=snippet,
                )
                tools.append(contract)
                return tres

            # 1. Evidence Search
            search_query = "Rahul Kumar" if "rahul" in query.lower() else query
            ev_res = await _run_tool("evidence_search", {"query": search_query}, "Searching Case Evidence")

            # 2. Entity Search
            ent_res = await _run_tool("entity_search", {"query": search_query}, "Searching Extracted Entities")

            # 3. Knowledge Graph
            kg_res = await _run_tool("knowledge_graph_traversal", {"entity": search_query, "max_depth": 2}, "Querying Case Knowledge Graph")
            if kg_res.results and isinstance(kg_res.results[0], dict):
                rels = kg_res.results[0].get("relationships", [])
                if rels:
                    detected_connection = rels[0]

            # 4. Vector Search if relevant
            if "semantic" in query.lower() or "connection" in query.lower() or "strongest" in query.lower():
                await _run_tool("vector_search", {"query": f"{search_query} evidence connection"}, "Semantic Vector Search")

            # 5. External Web Research if query requests public/external intelligence
            tavily_results = None
            if any(w in query.lower() for w in ("external", "public", "web", "corporate", "organization")):
                tav_res = await _run_tool("tavily_web_research", {"query": f"{search_query} corporate telecommunications India"}, "Tavily Web Research")
                tavily_results = tav_res.results

            if not collected_evidence_refs and ev_refs:
                collected_evidence_refs = ev_refs[:2]

            finding_title = "Strongest Evidence Connection: Rahul Kumar ↔ +91 9876543210" if detected_connection else "Verified Investigative Evidence Connection"
            desc_text = (
                f"Knowledge graph traversal and seized evidence {collected_evidence_refs[0] if collected_evidence_refs else 'EV-087'} "
                f"confirms connection between {detected_connection.get('source', 'Rahul Kumar')} and {detected_connection.get('target', '+91 9876543210')} "
                f"with relationship {detected_connection.get('relationship', 'OWNS_DEVICE')}."
            ) if detected_connection else (
                f"Investigative review of case {case_id} identified {len(collected_evidence_refs)} corroborating digital evidence items."
            )

            findings = [
                FindingContract(
                    id=f"find-{uuid.uuid4().hex[:6]}",
                    title=finding_title,
                    description=desc_text,
                    confidence=0.95,
                    status="needs_review",
                    agent_id="detective",
                    evidence_refs=collected_evidence_refs[:2],
                    subgraph_nodes=["Rahul Kumar", "+91 9876543210"] if detected_connection else None,
                )
            ]
            handoff = AgentHandoffContract(
                source_agent="detective",
                target_agent="timeline",
                reason="Discovered strong entity link that requires chronological event reconstruction.",
                context_summary="Sequence all communication timestamps between Rahul Kumar and the target number.",
            )
            src_conn = detected_connection.get('source', 'Rahul Kumar') if detected_connection else 'Rahul Kumar'
            rel_conn = detected_connection.get('relationship', 'OWNS_DEVICE') if detected_connection else 'OWNS_DEVICE'
            tgt_conn = detected_connection.get('target', '+91 9876543210') if detected_connection else '+91 9876543210'

            content = (
                f"As {agent_name}, I conducted a multi-stage forensic analysis across seized evidence in case {case_id}.\n\n"
                f"### Primary Forensic Evidence (Case-Scoped)\n"
                f"- **Seized Artifact**: {collected_evidence_refs[0] if collected_evidence_refs else 'EV-087'} (cdr_dump_jan2026.csv)\n"
                f"- **Verified Connection**: {src_conn} -[{rel_conn}]-> {tgt_conn}\n\n"
            )
            if tavily_results:
                t0 = tavily_results[0]
                content += (
                    f"### External Web Intelligence (EXTERNAL WEB SOURCE)\n"
                    f"> **Notice**: The following data is from an **EXTERNAL WEB SOURCE** and is NOT primary forensic evidence.\n"
                    f"- **Source**: {t0.get('source', 'tavily').upper()} ({t0.get('provenance', 'EXTERNAL WEB SOURCE')})\n"
                    f"- **Title**: {t0.get('title')}\n"
                    f"- **URL**: {t0.get('url')}\n"
                    f"- **Retrieved At**: {t0.get('retrieved_at')}\n"
                    f"- **Summary**: {t0.get('snippet')}\n"
                )
            else:
                content += (
                    f"### Investigation Conclusion\n"
                    f"Strongest verified connection established with evidence provenance {', '.join(collected_evidence_refs)}."
                )
            return AgentRuntimeResult(content, tools, findings, collected_evidence_refs[:2], 0.95, handoff)

        # ── 3. Timeline Agent ──
        elif agent_id == "timeline":
            tools = [
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="chrono_parser",
                    display_name="Parsing Normalized UTC Timestamps",
                    status="completed",
                    started_at=now,
                    completed_at=now + 0.1,
                    output_snippet="Normalized 14 timestamps across call logs and forensic image EXIF.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="temporal_sequence",
                    display_name="Reconstructing Event Chronology",
                    status="completed",
                    started_at=now + 0.1,
                    completed_at=now + 0.2,
                    output_snippet="Reconstructed chronological timeline between 21:00 UTC and 03:00 UTC.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="gap_analyzer",
                    display_name="Detecting Chronological Discrepancies",
                    status="completed",
                    started_at=now + 0.2,
                    completed_at=now + 0.3,
                    output_snippet="Identified a 42-minute communication blackout period.",
                ),
            ]
            findings = [
                FindingContract(
                    id=f"find-{uuid.uuid4().hex[:6]}",
                    title="Temporal Sequence & Blackout Window [DEMO DATA]",
                    description="Consistent incoming SMS sequence ends abruptly at 23:14 UTC, followed by a 42-minute transmission blackout.",
                    confidence=0.91,
                    status="needs_review",
                    agent_id="timeline",
                    evidence_refs=ev_refs[:2],
                )
            ]
            handoff = AgentHandoffContract(
                source_agent="timeline",
                target_agent="geoscope",
                reason="Identified 42-minute blackout window that warrants geospatial trajectory verification.",
                context_summary="Check cell tower locations and GPS waypoints during the 23:14 to 23:56 window.",
            )
            content = (
                f"[Phase 2 Backend Architecture]\n\n"
                f"As {agent_name}, I reconstructed chronological milestones for case {case_id}. "
                f"I mapped event sequences around query '{query}' and identified an unexplained activity gap. "
                f"Geospatial analysis should now verify cell tower connectivity during that window."
            )
            return AgentRuntimeResult(content, tools, findings, ev_refs[:2], 0.91, handoff)

        # ── 4. GeoScope Agent ──
        elif agent_id == "geoscope":
            tools = [
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="gps_extractor",
                    display_name="Extracting EXIF Coordinates & Cell Towers",
                    status="completed",
                    started_at=now,
                    completed_at=now + 0.1,
                    output_snippet="Located 5 geographic points with coordinate accuracy < 25m.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="cell_triangulation",
                    display_name="Triangulating Tower Coverage Sectors",
                    status="completed",
                    started_at=now + 0.1,
                    completed_at=now + 0.2,
                    output_snippet="Triangulated Sector CID 404-45-12019 near Industrial Zone.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="route_mapper",
                    display_name="Mapping Movement Trajectory",
                    status="completed",
                    started_at=now + 0.2,
                    completed_at=now + 0.3,
                    output_snippet="Traced waypoint trajectory moving along Highway 48 toward sector boundary.",
                ),
            ]
            findings = [
                FindingContract(
                    id=f"find-{uuid.uuid4().hex[:6]}",
                    title="Geospatial Proximity to Incident Perimeter [DEMO DATA]",
                    description="Extracted GPS coordinates and cell tower handoffs position the handset within 350m of the target site.",
                    confidence=0.89,
                    status="needs_review",
                    agent_id="geoscope",
                    evidence_refs=ev_refs[:2],
                )
            ]
            handoff = AgentHandoffContract(
                source_agent="geoscope",
                target_agent="testimony",
                reason="Geospatial route contradicts witness statement regarding suspect location.",
                context_summary="Cross-examine statement asserting suspect was 20km away with verified GPS coordinates.",
            )
            content = (
                f"[Phase 2 Backend Architecture]\n\n"
                f"As {agent_name}, I extracted location intelligence for case {case_id} regarding '{query}'. "
                f"Positioning logs place the target device in vicinity of the incident perimeter. "
                f"This location finding directly touches claims in witness statements."
            )
            return AgentRuntimeResult(content, tools, findings, ev_refs[:2], 0.89, handoff)

        # ── 5. Testimony Agent ──
        elif agent_id == "testimony":
            tools = [
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="claim_extractor",
                    display_name="Extracting Testimonial Claims",
                    status="completed",
                    started_at=now,
                    completed_at=now + 0.1,
                    output_snippet="Extracted 7 affirmative assertions from witness deposition.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="contradiction_detector",
                    display_name="Cross-Checking Claims Against Evidence",
                    status="completed",
                    started_at=now + 0.1,
                    completed_at=now + 0.2,
                    output_snippet="Flagged direct contradiction: Claimed alibi conflicts with tower ping.",
                ),
            ]
            findings = [
                FindingContract(
                    id=f"find-{uuid.uuid4().hex[:6]}",
                    title="Alibi Statement Contradiction [DEMO DATA]",
                    description="Suspect asserted non-presence in witness statement #2, but verified telecom tower records place handset at scene.",
                    confidence=0.96,
                    status="contradicted",
                    agent_id="testimony",
                    evidence_refs=ev_refs[:2],
                )
            ]
            handoff = AgentHandoffContract(
                source_agent="testimony",
                target_agent="evidence-review",
                reason="Critical contradiction identified; verify cryptographic integrity and chain of custody.",
                context_summary="Validate SHA-256 hash commitments on deposition audio and CDR dump.",
            )
            content = (
                f"[Phase 2 Backend Architecture]\n\n"
                f"As {agent_name}, I analyzed testimonial depositions in case {case_id} regarding '{query}'. "
                f"I detected a material contradiction between the stated alibi and forensic records. "
                f"Before entering this finding into the record, verify chain-of-custody integrity."
            )
            return AgentRuntimeResult(content, tools, findings, ev_refs[:2], 0.96, handoff)

        # ── 6. Evidence Review Agent ──
        elif agent_id == "evidence-review":
            tools = [
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="hash_verifier",
                    display_name="Verifying SHA-256 Hash Commitments",
                    status="completed",
                    started_at=now,
                    completed_at=now + 0.1,
                    output_snippet="SHA-256 hash matches original forensic capture commitment.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="custody_auditor",
                    display_name="Auditing Chain of Custody Ledger",
                    status="completed",
                    started_at=now + 0.1,
                    completed_at=now + 0.2,
                    output_snippet="Chain of Custody is unbroken across all transfers.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="admissibility_evaluator",
                    display_name="Checking Court Admissibility Standards",
                    status="completed",
                    started_at=now + 0.2,
                    completed_at=now + 0.3,
                    output_snippet="Admissibility criteria satisfied under Section 65B forensic rules.",
                ),
            ]
            findings = [
                FindingContract(
                    id=f"find-{uuid.uuid4().hex[:6]}",
                    title="Forensic Integrity & Custody Verified [DEMO DATA]",
                    description="All digital evidence files passed SHA-256 recalculation against Merkle root commitments with zero integrity flaws.",
                    confidence=0.99,
                    status="supported",
                    agent_id="evidence-review",
                    evidence_refs=ev_refs[:2],
                )
            ]
            handoff = AgentHandoffContract(
                source_agent="evidence-review",
                target_agent="report",
                reason="Evidence integrity certified; proceed with final court-ready report generation.",
                context_summary="Compile comprehensive case summary with certified evidence catalog.",
            )
            content = (
                f"[Phase 2 Backend Architecture]\n\n"
                f"As {agent_name}, I performed forensic integrity audits for case {case_id} on '{query}'. "
                f"All file hashes, timestamp records, and custody transitions remain verified. "
                f"The case is ready for synthetic report compilation."
            )
            return AgentRuntimeResult(content, tools, findings, ev_refs[:2], 0.99, handoff)

        # ── 7. Report Agent ──
        else:
            tools = [
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="report_compiler",
                    display_name="Compiling Multi-Agent Findings",
                    status="completed",
                    started_at=now,
                    completed_at=now + 0.1,
                    output_snippet="Aggregated findings from Orchestrator, Detective, Timeline, GeoScope, and Review.",
                ),
                ToolExecutionContract(
                    id=f"tool-{uuid.uuid4().hex[:6]}",
                    tool_name="evidence_catalog",
                    display_name="Generating Court Evidence Exhibit Catalog",
                    status="completed",
                    started_at=now + 0.1,
                    completed_at=now + 0.2,
                    output_snippet="Generated forensic exhibit table with hashes and timestamp audit.",
                ),
            ]
            findings = [
                FindingContract(
                    id=f"find-{uuid.uuid4().hex[:6]}",
                    title="Court-Admissible Investigation Synthesis [DEMO DATA]",
                    description="Comprehensive case brief compiled with 12 cited exhibits, verified chain of custody, and timeline exhibits.",
                    confidence=0.95,
                    status="supported",
                    agent_id="report",
                    evidence_refs=ev_refs[:2],
                )
            ]
            content = (
                f"[Phase 2 Backend Architecture]\n\n"
                f"As {agent_name}, I synthesized the complete multi-agent investigation file for case {case_id} regarding '{query}'. "
                f"I incorporated timeline chronologies, geospatial findings, and verified chain-of-custody audits. "
                f"Court-ready exhibit exhibits are prepared."
            )
            return AgentRuntimeResult(content, tools, findings, ev_refs[:2], 0.95, None)


class NebiusNemotronRuntime(BaseAgentRuntime):
    """
    Production-oriented Nebius + NVIDIA Nemotron Agent Runtime.

    Passes queries through the centralized Nebius Token Factory model gateway.
    Specializes Detective Agent with deep forensic system prompt and context window management.
    Falls back gracefully if provider is unconfigured or unavailable.
    """

    def __init__(
        self,
        provider: Optional[BaseModelProvider] = None,
        mock_fallback: Optional[BaseAgentRuntime] = None,
        tool_registry: Optional[Any] = None,
        max_history_turns: int = 6,
        max_tool_rounds: int = 4,
    ):
        from .nebius_provider import NebiusNemotronProvider
        from .tools import get_tool_registry
        self.provider = provider or NebiusNemotronProvider()
        self.mock_fallback = mock_fallback or MockDeterministicAgentRuntime()
        self.tool_registry = tool_registry or get_tool_registry()
        self.max_history_turns = max_history_turns
        self.max_tool_rounds = max_tool_rounds

    async def execute_turn(
        self,
        agent_id: str,
        case_id: str,
        query: str,
        session_id: str,
        history: List[Dict[str, Any]],
        case_evidence_refs: Optional[List[str]] = None,
    ) -> AgentRuntimeResult:
        from .gateway import ModelRequest, ModelMessage, ProviderError, ProviderNotConfiguredError
        from .detective_prompt import build_detective_prompt
        import json
        import re

        # For Phase 6/7/8: Case Orchestrator, Detective, Timeline, GeoScope, Report, and Testimony Agents use the real gateway & orchestration.
        # Other agents will be onboarded in subsequent phases.
        supported_real_agents = {"case-orchestrator", "detective", "timeline", "geoscope", "report", "testimony"}
        if agent_id not in supported_real_agents:
            return await self.mock_fallback.execute_turn(
                agent_id=agent_id,
                case_id=case_id,
                query=query,
                session_id=session_id,
                history=history,
                case_evidence_refs=case_evidence_refs,
            )

        # ── Handle Case Orchestrator multi-agent coordination ──
        if agent_id == "case-orchestrator":
            if not self.provider.is_configured:
                return AgentRuntimeResult(
                    content=(
                        "AI model provider is not configured. Please set NEBIUS_API_KEY in the backend "
                        "environment to enable NVIDIA Nemotron reasoning."
                    ),
                    tool_executions=[
                        ToolExecutionContract(
                            id=f"tool-{uuid.uuid4().hex[:6]}",
                            tool_name="nebius_gateway",
                            display_name="Nebius Token Factory Gateway",
                            status="failed",
                            output_snippet="NEBIUS_API_KEY not set in backend environment.",
                        )
                    ],
                    findings=[],
                    evidence_refs=case_evidence_refs[:2] if case_evidence_refs else [],
                    confidence=None,
                    handoff=None,
                )

            from .orchestration_service import CaseOrchestratorService
            orchestrator_service = CaseOrchestratorService(
                provider=self.provider,
                specialist_runtime=self,
                tool_registry=self.tool_registry,
            )
            return await orchestrator_service.execute_orchestration_turn(
                case_id=case_id,
                query=query,
                session_id=session_id,
                history=history,
                case_evidence_refs=case_evidence_refs,
            )

        # If provider credentials are not configured, return clear non-fatal status
        if not self.provider.is_configured:
            return AgentRuntimeResult(
                content=(
                    "AI model provider is not configured. Please set NEBIUS_API_KEY in the backend "
                    "environment to enable NVIDIA Nemotron reasoning."
                ),
                tool_executions=[
                    ToolExecutionContract(
                        id=f"tool-{uuid.uuid4().hex[:6]}",
                        tool_name="nebius_gateway",
                        display_name="Nebius Token Factory Gateway",
                        status="failed",
                        output_snippet="NEBIUS_API_KEY not set in backend environment.",
                    )
                ],
                findings=[],
                evidence_refs=case_evidence_refs[:2] if case_evidence_refs else [],
                confidence=None,
                handoff=None,
            )

        # Build context-managed conversation history (last N messages)
        recent_history = history[-self.max_history_turns:] if history else []
        model_messages = [
            ModelMessage(role=m.get("role", "user"), content=m.get("content", ""))
            for m in recent_history
            if m.get("role") in ("user", "assistant")
        ]
        # Append current user prompt
        model_messages.append(ModelMessage(role="user", content=query))

        # Select agent-specific system prompt and tool scope
        from .specialist_prompts import build_timeline_prompt, build_geoscope_prompt, build_report_prompt, build_testimony_prompt
        if agent_id == "timeline":
            system_prompt = build_timeline_prompt(case_id, case_evidence_refs)
            openai_tools = self.tool_registry.get_openai_tools_for_agent("timeline")
        elif agent_id == "geoscope":
            system_prompt = build_geoscope_prompt(case_id, case_evidence_refs)
            openai_tools = self.tool_registry.get_openai_tools_for_agent("geoscope")
        elif agent_id == "report":
            system_prompt = build_report_prompt(case_id, case_evidence_refs)
            openai_tools = []
        elif agent_id == "testimony":
            system_prompt = build_testimony_prompt(case_id, case_evidence_refs)
            # Testimony specialist has access to cross-check tools
            openai_tools = (
                self.tool_registry.get_openai_tools_for_agent("timeline")
                + self.tool_registry.get_openai_tools_for_agent("geoscope")
                + self.tool_registry.get_openai_tools_for_agent("detective")[:1]
            )
        else:
            system_prompt = build_detective_prompt(case_id, case_evidence_refs)
            openai_tools = self.tool_registry.get_openai_tools_for_agent("detective")

        tool_executions_log: List[ToolExecutionContract] = []
        collected_evidence_refs: List[str] = list(case_evidence_refs or [])[:2] if case_evidence_refs else []
        round_count = 0
        final_text = ""

        # Domain events publisher helper
        def _emit_event(event_type: str, data: Dict[str, Any]):
            try:
                from ...events import DomainEvent, publish_event
                ev = DomainEvent(event_type=event_type, case_id=case_id, metadata=data)
                publish_event(ev)
            except Exception:
                pass

        try:
            while round_count < self.max_tool_rounds:
                round_count += 1
                req = ModelRequest(
                    messages=model_messages,
                    system_prompt=system_prompt,
                    temperature=0.2,
                    max_tokens=1200,
                    tools=openai_tools,
                )
                model_start = time.time()
                _emit_event("model.requested", {
                    "case_id": case_id,
                    "session_id": session_id,
                    "agent": agent_id,
                    "model": getattr(self.provider, "model_name", "nvidia/nemotron-4-340b-instruct"),
                    "round": round_count,
                    "timestamp": model_start,
                })

                try:
                    resp = await self.provider.chat(req)
                    model_lat = (time.time() - model_start) * 1000
                    _emit_event("model.completed", {
                        "case_id": case_id,
                        "session_id": session_id,
                        "agent": agent_id,
                        "model": getattr(self.provider, "model_name", "nvidia/nemotron-4-340b-instruct"),
                        "latency": round(model_lat, 2),
                        "tokens": getattr(resp.usage, "total_tokens", 0) if resp.usage else 0,
                        "tool_call_count": len(resp.tool_calls or []),
                        "timestamp": time.time(),
                    })
                except Exception as m_exc:
                    _emit_event("model.failed", {
                        "case_id": case_id,
                        "session_id": session_id,
                        "agent": agent_id,
                        "model": getattr(self.provider, "model_name", "nvidia/nemotron-4-340b-instruct"),
                        "latency": round((time.time() - model_start) * 1000, 2),
                        "error": str(m_exc),
                        "timestamp": time.time(),
                    })
                    raise

                # Check for tool calls either in structured tool_calls or in text
                detected_calls = []
                if resp.tool_calls:
                    for tc in resp.tool_calls:
                        fn = tc.get("function", {})
                        t_name = fn.get("name")
                        t_args = fn.get("arguments")
                        if isinstance(t_args, str):
                            try:
                                t_args = json.loads(t_args)
                            except Exception:
                                t_args = {}
                        if t_name:
                            detected_calls.append({"name": t_name, "arguments": t_args or {}})
                else:
                    # Check text for ```tool_call blocks
                    raw_text = resp.content or ""
                    match = re.search(r"```(?:tool_call|json)?\s*(\{\s*\"name\"[\s\S]*?\})\s*```", raw_text)
                    if match:
                        try:
                            parsed = json.loads(match.group(1))
                            if "name" in parsed:
                                detected_calls.append({
                                    "name": parsed["name"],
                                    "arguments": parsed.get("arguments", {}),
                                })
                        except Exception:
                            pass

                # If no tool calls detected or final response reached, exit loop
                if not detected_calls:
                    final_text = resp.content
                    # If no tools were invoked during this turn, record the gateway inference execution
                    if not tool_executions_log:
                        gateway_tool = ToolExecutionContract(
                            id=f"tool-{uuid.uuid4().hex[:6]}",
                            tool_name="nebius_nemotron_gateway",
                            display_name=f"Querying {self.provider.model_name} via Nebius",
                            status="completed",
                            started_at=time.time() - 0.2,
                            completed_at=time.time(),
                            output_snippet=f"Generated {resp.usage.completion_tokens} tokens using {self.provider.model_name}.",
                        )
                        tool_executions_log.append(gateway_tool)
                    break

                # Execute detected tools in CrimeKit ToolRegistry
                for tc in detected_calls:
                    t_name = tc["name"]
                    t_args = tc.get("arguments", {})
                    t_label = t_name.replace("_", " ").title()

                    tool_exec_contract = ToolExecutionContract(
                        id=f"tool-{uuid.uuid4().hex[:6]}",
                        tool_name=t_name,
                        display_name=t_label,
                        status="running",
                        started_at=time.time(),
                    )
                    tool_executions_log.append(tool_exec_contract)
                    _emit_event("tool.started", {"tool_name": t_name, "case_id": case_id, "agent_id": agent_id})

                    # Execute tool against authorized case
                    t_result = await self.tool_registry.execute(
                        tool_name=t_name,
                        case_id=case_id,
                        user_id=f"{agent_id}-agent",
                        arguments=t_args,
                        context={"agent": agent_id, "session_id": session_id},
                    )

                    tool_exec_contract.completed_at = time.time()
                    if t_result.status == "completed":
                        tool_exec_contract.status = "completed"
                        tool_exec_contract.output_snippet = (
                            f"Returned {t_result.result_count} items in {t_result.duration_ms}ms."
                        )
                        _emit_event("tool.completed", {
                            "tool_name": t_name,
                            "case_id": case_id,
                            "agent_id": agent_id,
                            "result_count": t_result.result_count,
                        })
                        for eref in t_result.evidence_refs:
                            if eref and eref not in collected_evidence_refs:
                                collected_evidence_refs.append(eref)
                    else:
                        tool_exec_contract.status = "failed"
                        tool_exec_contract.output_snippet = t_result.error_message or "Tool execution failed."
                        _emit_event("tool.failed", {
                            "tool_name": t_name,
                            "case_id": case_id,
                            "agent_id": agent_id,
                            "error": t_result.error_message,
                        })

                    # Append model message turn with tool result
                    model_messages.append(ModelMessage(
                        role="assistant",
                        content=f"Invoking {t_name} with parameters: {json.dumps(t_args)}",
                    ))
                    model_messages.append(ModelMessage(
                        role="system",
                        content=(
                            f"TOOL EXECUTION RESULT FOR {t_name}:\n"
                            f"Status: {t_result.status}\n"
                            f"Count: {t_result.result_count}\n"
                            f"Evidence IDs Found: {', '.join(t_result.evidence_refs) if t_result.evidence_refs else 'None'}\n"
                            f"Data: {json.dumps(t_result.results[:5])}\n"
                            "Synthesize findings based strictly on the above returned facts. Do not invent any outside facts."
                        ),
                    ))

            if not final_text:
                final_text = resp.content

            # Structured Findings extraction based on verified evidence citations
            findings: List[FindingContract] = []
            verified_refs = [
                e for e in (case_evidence_refs or [])
                if e in final_text or e in collected_evidence_refs
            ]
            if not verified_refs and collected_evidence_refs:
                verified_refs = collected_evidence_refs[:3]

            # Generate structured finding if specialist tools completed successfully
            completed_tools = [t.tool_name for t in tool_executions_log if t.status == "completed"]
            if completed_tools:
                finding_title = "Verified Forensic Finding"
                if agent_id == "timeline":
                    finding_title = "Verified Chronological Timeline Finding"
                elif agent_id == "geoscope":
                    finding_title = "Verified Geospatial Location Finding"
                elif agent_id == "detective":
                    finding_title = "Verified Investigative Finding"

                findings.append(FindingContract(
                    id=f"find-{uuid.uuid4().hex[:6]}",
                    title=finding_title,
                    description=(
                        final_text[:180] + "..." if len(final_text) > 180 else final_text
                    ),
                    confidence=0.91,
                    status="needs_review",
                    agent_id=agent_id,
                    evidence_refs=verified_refs[:3],
                ))
                _emit_event("finding.created", {
                    "case_id": case_id,
                    "agent_id": agent_id,
                    "finding_title": finding_title,
                })

            # Detect potential handoff recommendations in text
            handoff: Optional[AgentHandoffContract] = None
            lower_content = final_text.lower()
            if agent_id == "detective":
                if any(w in lower_content for w in ("timeline", "temporal", "chronolog")):
                    handoff = AgentHandoffContract(
                        source_agent="detective",
                        target_agent="timeline",
                        reason="Detective Agent noted temporal aspects that may benefit from Chronology Analysis.",
                        context_summary="Sequence timestamps discussed in query.",
                    )
                elif any(w in lower_content for w in ("location", "gps", "geoscope", "coordinates", "movement")):
                    handoff = AgentHandoffContract(
                        source_agent="detective",
                        target_agent="geoscope",
                        reason="Detective Agent noted geospatial aspects that may benefit from Location Intelligence.",
                        context_summary="Analyze GPS/EXIF coordinates from case evidence.",
                    )
            elif agent_id == "timeline":
                if any(w in lower_content for w in ("location", "gps", "geoscope", "co-location", "where")):
                    handoff = AgentHandoffContract(
                        source_agent="timeline",
                        target_agent="geoscope",
                        reason="Timeline Agent identified events requiring spatial/geographic positioning.",
                        context_summary="Correlate timestamps with GPS/EXIF coordinates.",
                    )
            elif agent_id == "geoscope":
                if any(w in lower_content for w in ("timeline", "sequence", "before", "after", "hour", "minute")):
                    handoff = AgentHandoffContract(
                        source_agent="geoscope",
                        target_agent="timeline",
                        reason="GeoScope Agent noted movement points requiring temporal sequence reconstruction.",
                        context_summary="Align waypoints along minute-by-minute timeline.",
                    )

            return AgentRuntimeResult(
                content=final_text,
                tool_executions=tool_executions_log,
                findings=findings,
                evidence_refs=verified_refs,
                confidence=0.92 if verified_refs else None,
                handoff=handoff,
            )


        except ProviderError as p_err:
            err_tool = ToolExecutionContract(
                id=f"tool-{uuid.uuid4().hex[:6]}",
                tool_name="nebius_nemotron_gateway",
                display_name=f"Querying {self.provider.model_name}",
                status="failed",
                started_at=time.time(),
                completed_at=time.time(),
                output_snippet=p_err.message,
            )
            return AgentRuntimeResult(
                content=f"Error: {p_err.message}",
                tool_executions=[err_tool],
                findings=[],
                evidence_refs=[],
                confidence=None,
                handoff=None,
            )


# Default singleton runtime instances
mock_runtime = MockDeterministicAgentRuntime()
nebius_runtime = NebiusNemotronRuntime(mock_fallback=mock_runtime)


def get_agent_runtime() -> BaseAgentRuntime:
    """
    Return configured agent runtime.
    Uses NebiusNemotronRuntime as default in Phase 3.
    Can be overridden via AGENT_RUNTIME_MODE=mock for testing.
    """
    import os
    mode = os.getenv("AGENT_RUNTIME_MODE", "nebius").lower()
    if mode == "mock":
        return mock_runtime
    return nebius_runtime

