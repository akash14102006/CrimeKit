import type { LucideIcon } from "lucide-react";
import {
  BrainCircuit,
  SearchCheck,
  Clock3,
  MapPinned,
  MessageSquareQuote,
  FileText,
  ShieldCheck,
} from "lucide-react";

export type AgentId =
  | "case-orchestrator"
  | "detective"
  | "timeline"
  | "geoscope"
  | "testimony"
  | "evidence-review"
  | "report";

export interface AgentDefinition {
  id: AgentId;
  name: string;
  shortName: string;
  tagline: string;
  description: string;
  icon: LucideIcon;
  category: "orchestration" | "investigation" | "temporal" | "geospatial" | "forensics" | "synthesis";
  status: "ready" | "running" | "idle" | "offline";
  model: string;
  tools: string[];
  suggestedQuestions: string[];
  capabilities: string[];
}

export const AGENT_REGISTRY: Record<AgentId, AgentDefinition> = {
  "case-orchestrator": {
    id: "case-orchestrator",
    name: "Case Orchestrator",
    shortName: "Orchestrator",
    tagline: "Coordinates multi-agent investigation workflows",
    description:
      "Supervises the full investigation lifecycle, delegates tasks to specialist agents, synthesizes cross-domain findings, and maintains case direction.",
    icon: BrainCircuit,
    category: "orchestration",
    status: "ready",
    model: "NVIDIA Nemotron (Orchestrator Mode)",
    tools: [
      "Specialist Delegation",
      "Finding Synthesis",
      "Contradiction Detection",
      "Evidence Catalog",
    ],
    suggestedQuestions: [
      "What are the top priority leads in this case?",
      "Delegate a comprehensive evidence review across all files",
      "Provide an executive synthesis of current findings and gaps",
      "Coordinate timeline and location cross-checks for suspects",
    ],
    capabilities: [
      "multi-agent-orchestration",
      "case-synthesis",
      "task-delegation",
      "gap-analysis",
    ],
  },
  detective: {
    id: "detective",
    name: "Detective Agent",
    shortName: "Detective",
    tagline: "Evidence correlation and entity relationship discovery",
    description:
      "Discovers latent relationships, cross-references suspects, phone numbers, and organizations across digital evidence, and builds subgraph connections.",
    icon: SearchCheck,
    category: "investigation",
    status: "ready",
    model: "NVIDIA Nemotron (Investigation Specialist)",
    tools: [
      "Evidence Search",
      "Entity Search",
      "Knowledge Graph Query",
      "Vector Semantic RAG",
    ],
    suggestedQuestions: [
      "Find all connections between Rahul Kumar and phone +91 9876543210",
      "What evidence items mention bank account numbers or wire transfers?",
      "Trace entity relationships around the primary suspect",
      "Identify high-centrality nodes and communication clusters",
    ],
    capabilities: [
      "evidence-correlation",
      "entity-extraction",
      "graph-analytics",
      "vector-search",
    ],
  },
  timeline: {
    id: "timeline",
    name: "Timeline Agent",
    shortName: "Timeline",
    tagline: "Chronological event reconstruction & temporal analysis",
    description:
      "Reconstructs minute-by-minute temporal chronologies from EXIF timestamps, email headers, call detail records (CDRs), and forensic file metadata.",
    icon: Clock3,
    category: "temporal",
    status: "ready",
    model: "NVIDIA Nemotron (Chronology Specialist)",
    tools: [
      "Timestamp Extractor",
      "Sequence Reconstruction",
      "Temporal Anomaly Detector",
      "CDR Timeline Parser",
    ],
    suggestedQuestions: [
      "Build a minute-by-minute timeline for the day of the incident",
      "What events occurred between 22:00 and 02:00 on the target date?",
      "Identify temporal gaps or timestamp inconsistencies across evidence",
      "Correlate communication timestamps with financial transfer times",
    ],
    capabilities: [
      "temporal-reconstruction",
      "anomaly-detection",
      "cdr-analysis",
      "chronological-ordering",
    ],
  },
  geoscope: {
    id: "geoscope",
    name: "GeoScope Agent",
    shortName: "GeoScope",
    tagline: "Location intelligence & movement pattern analysis",
    description:
      "Extracts GPS coordinates from image EXIF, IP geolocation logs, cell tower IDs, and movement waypoints to establish whereabouts and route patterns.",
    icon: MapPinned,
    category: "geospatial",
    status: "ready",
    model: "NVIDIA Nemotron (GeoSpatial Specialist)",
    tools: [
      "GPS Coordinate Parser",
      "Cell Tower Triangulation",
      "Proximity Analysis",
      "Movement Route Mapper",
    ],
    suggestedQuestions: [
      "Extract all GPS coordinates from image and video evidence",
      "Identify locations where multiple suspects were co-present",
      "Trace the suspect's movement trajectory leading up to the event",
      "Compare location coordinates with timeline event timestamps",
    ],
    capabilities: [
      "geospatial-clustering",
      "movement-tracking",
      "co-location-detection",
      "exif-mapping",
    ],
  },
  testimony: {
    id: "testimony",
    name: "Testimony Agent",
    shortName: "Testimony",
    tagline: "Statement analysis & contradiction detection",
    description:
      "Analyzes witness testimonies, interrogation transcripts, and written affidavits to cross-verify claims against verified forensic evidence.",
    icon: MessageSquareQuote,
    category: "investigation",
    status: "ready",
    model: "NVIDIA Nemotron (Testimony Specialist)",
    tools: [
      "Claim Extractor",
      "Timeline Cross-Check",
      "Location Cross-Check",
      "Alibi Verifier",
      "Contradiction Detector",
    ],
    suggestedQuestions: [
      "Extract all factual claims from this witness statement",
      "Cross-check witness statement against the case timeline and call logs",
      "Verify the suspect's alibi against recorded device locations",
      "Identify contradictions between this testimony and forensic evidence",
    ],
    capabilities: [
      "claim-extraction",
      "contradiction-analysis",
      "alibi-verification",
      "inconsistency-flagging",
    ],
  },
  "evidence-review": {
    id: "evidence-review",
    name: "Evidence Review Agent",
    shortName: "Evidence Review",
    tagline: "Forensic validation & chain of custody integrity",
    description:
      "Validates forensic integrity, verifies SHA-256 hash commitments, audits Chain of Custody ledger records, and flags admissibility risks.",
    icon: ShieldCheck,
    category: "forensics",
    status: "ready",
    model: "NVIDIA Nemotron (Forensic Integrity Specialist)",
    tools: [
      "SHA-256 Hash Verifier",
      "Chain of Custody Auditor",
      "File Format Validator",
      "Admissibility Risk Checker",
    ],
    suggestedQuestions: [
      "Verify SHA-256 hashes and integrity across all uploaded evidence",
      "Audit the complete chain of custody for missing custody handoffs",
      "Flag any evidence items with missing provenance or tamper indicators",
      "Assess whether current forensic extractions meet court admissibility criteria",
    ],
    capabilities: [
      "hash-verification",
      "custody-audit",
      "integrity-verification",
      "court-admissibility-check",
    ],
  },
  report: {
    id: "report",
    name: "Report Agent",
    shortName: "Report",
    tagline: "Investigation synthesis & court-ready report generation",
    description:
      "Synthesizes multi-agent findings, verified evidence citations, timeline events, and entity matrices into court-admissible forensic investigation reports.",
    icon: FileText,
    category: "synthesis",
    status: "ready",
    model: "NVIDIA Nemotron (Report Specialist)",
    tools: [
      "Forensic Report Compiler",
      "Court Summary Formatter",
      "Evidence Catalog Generator",
      "Legal Compliance Validator",
    ],
    suggestedQuestions: [
      "Generate an executive forensic summary of this entire investigation",
      "Create a court-ready evidence catalog with hashes and chain of custody",
      "Compile a comprehensive timeline exhibit with cited evidence attachments",
      "Summarize unresolved questions and open investigative leads",
    ],
    capabilities: [
      "report-generation",
      "evidence-cataloging",
      "court-ready-formatting",
      "executive-summaries",
    ],
  },
};

export const AGENT_LIST: AgentDefinition[] = Object.values(AGENT_REGISTRY);

export function getAgent(id: string | null | undefined): AgentDefinition {
  if (id && id in AGENT_REGISTRY) {
    return AGENT_REGISTRY[id as AgentId];
  }
  return AGENT_REGISTRY["detective"];
}
