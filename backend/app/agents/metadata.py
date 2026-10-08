"""
Centralized Canonical Backend Agent Registry.

Single source of truth for CrimeKit AI Specialist Agents:
- case-orchestrator
- detective
- timeline
- geoscope
- testimony
- evidence-review
- report
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AgentMetadata(BaseModel):
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Full display name")
    short_name: str = Field(..., description="Short tag name")
    tagline: str = Field(..., description="Single-line value statement")
    description: str = Field(..., description="Detailed role description")
    icon: str = Field(..., description="Emoji/icon symbol")
    category: str = Field(..., description="investigation | orchestration | temporal | geospatial | forensics | synthesis")
    status: str = Field(default="ready", description="Operational status: ready, running, offline")
    capabilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    suggested_questions: List[str] = Field(default_factory=list)


CANONICAL_AGENTS: Dict[str, AgentMetadata] = {
    "case-orchestrator": AgentMetadata(
        id="case-orchestrator",
        name="Case Orchestrator",
        short_name="Orchestrator",
        tagline="Coordinates multi-agent investigation workflows",
        description="Supervises the full investigation lifecycle, delegates tasks to specialist agents, synthesizes cross-domain findings, and maintains case direction.",
        icon="🧠",
        category="orchestration",
        status="ready",
        capabilities=["multi-agent-orchestration", "case-synthesis", "task-delegation", "gap-analysis"],
        tools=["Agent Delegation", "Case Status Audit", "Conflict Resolution", "Executive Briefing"],
        suggested_questions=[
            "What are the top priority leads in this case?",
            "Delegate a comprehensive evidence review across all files",
            "Provide an executive synthesis of current findings and gaps",
            "Coordinate timeline and location cross-checks for suspects",
        ],
    ),
    "detective": AgentMetadata(
        id="detective",
        name="Detective Agent",
        short_name="Detective",
        tagline="Evidence correlation and entity relationship discovery",
        description="Discovers latent relationships, cross-references suspects, phone numbers, and organizations across digital evidence, and builds subgraph connections.",
        icon="🔍",
        category="investigation",
        status="ready",
        capabilities=["evidence-search", "entity-search", "knowledge-graph", "vector-search", "evidence-correlation"],
        tools=["Evidence Search", "Entity Search", "Knowledge Graph Query", "Vector Semantic RAG"],
        suggested_questions=[
            "Find all connections between Rahul Kumar and phone +91 9876543210",
            "What evidence items mention bank account numbers or wire transfers?",
            "Trace entity relationships around the primary suspect",
            "Identify high-centrality nodes and communication clusters",
        ],
    ),
    "timeline": AgentMetadata(
        id="timeline",
        name="Timeline Agent",
        short_name="Timeline",
        tagline="Chronological event reconstruction & temporal analysis",
        description="Reconstructs minute-by-minute temporal chronologies from EXIF timestamps, email headers, call detail records (CDRs), and forensic file metadata.",
        icon="◷",
        category="temporal",
        status="ready",
        capabilities=["temporal-reconstruction", "anomaly-detection", "cdr-analysis", "chronological-ordering"],
        tools=["Timestamp Extractor", "Sequence Reconstruction", "Temporal Anomaly Detector", "CDR Timeline Parser"],
        suggested_questions=[
            "Build a minute-by-minute timeline for the day of the incident",
            "What events occurred between 22:00 and 02:00 on the target date?",
            "Identify temporal gaps or timestamp inconsistencies across evidence",
            "Correlate communication timestamps with financial transfer times",
        ],
    ),
    "geoscope": AgentMetadata(
        id="geoscope",
        name="GeoScope Agent",
        short_name="GeoScope",
        tagline="Location intelligence & movement pattern analysis",
        description="Extracts GPS coordinates from image EXIF, IP geolocation logs, cell tower IDs, and movement waypoints to establish whereabouts and route patterns.",
        icon="📍",
        category="geospatial",
        status="ready",
        capabilities=["geospatial-clustering", "movement-tracking", "co-location-detection", "exif-mapping"],
        tools=["GPS Coordinate Parser", "Cell Tower Triangulation", "Proximity Analysis", "Movement Route Mapper"],
        suggested_questions=[
            "Extract all GPS coordinates from image and video evidence",
            "Identify locations where multiple suspects were co-present",
            "Trace the suspect's movement trajectory leading up to the event",
            "Compare location coordinates with timeline event timestamps",
        ],
    ),
    "testimony": AgentMetadata(
        id="testimony",
        name="Testimony Agent",
        short_name="Testimony",
        tagline="Statement analysis & contradiction detection",
        description="Analyzes witness testimonies, interrogation transcripts, and written affidavits to cross-verify claims against verified forensic evidence.",
        icon="💬",
        category="investigation",
        status="ready",
        capabilities=["claim-extraction", "contradiction-analysis", "alibi-verification", "inconsistency-flagging"],
        tools=["Claim Extractor", "Contradiction Detector", "Alibi Verifier", "Sentiment & Stress Markers"],
        suggested_questions=[
            "Extract all factual claims from witness statement #1",
            "Check the suspect's alibi against verified timestamped evidence",
            "Identify contradictions between statements given by witness A and witness B",
            "Highlight statements that directly conflict with phone CDR records",
        ],
    ),
    "evidence-review": AgentMetadata(
        id="evidence-review",
        name="Evidence Review Agent",
        short_name="Evidence Review",
        tagline="Forensic validation & chain of custody integrity",
        description="Validates forensic integrity, verifies SHA-256 hash commitments, audits Chain of Custody ledger records, and flags admissibility risks.",
        icon="✓",
        category="forensics",
        status="ready",
        capabilities=["hash-verification", "custody-audit", "integrity-verification", "court-admissibility-check"],
        tools=["SHA-256 Hash Verifier", "Chain of Custody Auditor", "File Format Validator", "Admissibility Risk Checker"],
        suggested_questions=[
            "Verify SHA-256 hashes and integrity across all uploaded evidence",
            "Audit the complete chain of custody for missing custody handoffs",
            "Flag any evidence items with missing provenance or tamper indicators",
            "Assess whether current forensic extractions meet court admissibility criteria",
        ],
    ),
    "report": AgentMetadata(
        id="report",
        name="Report Agent",
        short_name="Report",
        tagline="Investigation synthesis & court-ready report generation",
        description="Synthesizes multi-agent findings, verified evidence citations, timeline events, and entity matrices into court-admissible forensic investigation reports.",
        icon="📄",
        category="synthesis",
        status="ready",
        capabilities=["report-generation", "evidence-cataloging", "court-ready-formatting", "executive-summaries"],
        tools=["Forensic Report Compiler", "Court Summary Formatter", "Evidence Catalog Generator", "Legal Compliance Validator"],
        suggested_questions=[
            "Generate an executive forensic summary of this entire investigation",
            "Create a court-ready evidence catalog with hashes and chain of custody",
            "Compile a comprehensive timeline exhibit with cited evidence attachments",
            "Summarize unresolved questions and open investigative leads",
        ],
    ),
}


def get_agent_metadata(agent_id: str) -> Optional[AgentMetadata]:
    """Retrieve canonical metadata for a given agent ID."""
    return CANONICAL_AGENTS.get(agent_id)


def is_valid_agent_id(agent_id: str) -> bool:
    """Validate whether an agent ID is recognized by the canonical registry."""
    return agent_id in CANONICAL_AGENTS


def list_agents_metadata() -> List[AgentMetadata]:
    """List all registered agents."""
    return list(CANONICAL_AGENTS.values())
