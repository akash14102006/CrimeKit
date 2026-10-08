import type { AgentId } from "../constants/agentRegistry";
import type { ToolExecution, AIFinding, AgentHandoff, AICitation } from "../store/aiStore";

export interface MockAgentResponse {
  content: string;
  toolExecutions: ToolExecution[];
  findings?: AIFinding[];
  citations?: AICitation[];
  evidence_refs?: string[];
  confidence: number;
  handoff?: AgentHandoff;
}

export function generateMockAgentResponse(
  agentId: AgentId,
  userPrompt: string,
  caseId?: string,
): MockAgentResponse {
  const cId = caseId || "CK-2026-021";
  const now = Date.now();

  switch (agentId) {
    case "detective":
      return {
        content: `I've analyzed the case evidence and cross-referenced entity graphs for "${userPrompt}".

Identified a key correlation between the target entity and phone records in the evidence locker. Communication frequency peaked during the critical investigation window, supported by mutual association in document disclosures.`,
        toolExecutions: [
          { id: "t1", tool: "Evidence Search", label: `Searching Case ${cId} evidence files`, status: "completed" },
          { id: "t2", tool: "Entity Extraction", label: "Extracting names, phone numbers, and accounts", status: "completed" },
          { id: "t3", tool: "Knowledge Graph", label: "Querying Neo4j entity-relationship subgraphs", status: "completed" },
          { id: "t4", tool: "Correlation Analysis", label: "Computing mutual centrality & link confidence", status: "completed" },
        ],
        findings: [
          {
            id: `find-${now}-1`,
            title: "Entity Correlation: Rahul Kumar ↔ +91 9876543210",
            description: "Direct telecommunication link detected across 14 call records and 3 encrypted chat logs within Case evidence.",
            confidence: 0.94,
            evidenceRefs: ["EV-087", "EV-104"],
            agentId: "detective",
            status: "verified",
          },
        ],
        citations: [
          { id: "c1", type: "evidence", label: "EV-087 (Phone Extraction Report)", source_id: "EV-087", confidence: 0.95 },
          { id: "c2", type: "kg", label: "Neo4j Relation: COMMUNICATED_WITH", confidence: 0.92 },
        ],
        evidence_refs: ["EV-087", "EV-104"],
        confidence: 0.94,
        handoff: {
          targetAgentId: "timeline",
          reason: "High-confidence communications detected. A temporal reconstruction of call sequences around the incident window is recommended.",
          contextSummary: "Correlated Rahul Kumar with +91 9876543210 across EV-087 & EV-104.",
        },
      };

    case "timeline":
      return {
        content: `I've reconstructed the temporal chronology surrounding "${userPrompt}".

Chronological clustering reveals 4 distinct events between 22:15 and 01:45. A significant 90-minute blackout in communication logs precedes the primary incident timestamp.`,
        toolExecutions: [
          { id: "t1", tool: "Timestamp Extractor", label: "Parsing EXIF and CDR timestamps", status: "completed" },
          { id: "t2", tool: "Sequence Reconstruction", label: "Ordering events chronologically", status: "completed" },
          { id: "t3", tool: "Anomaly Detection", label: "Detecting communication inactivity intervals", status: "completed" },
        ],
        findings: [
          {
            id: `find-${now}-2`,
            title: "Temporal Anomaly: 90-Minute Device Blackout",
            description: "Device active until 22:42 IST, went dark during incident window, and reconnected to cell tower at 00:14 IST.",
            confidence: 0.91,
            evidenceRefs: ["EV-104", "EV-112"],
            agentId: "timeline",
            status: "needs-review",
          },
        ],
        citations: [
          { id: "c1", type: "timeline", label: "Event Seq #14: Final Outgoing Call (22:42)", confidence: 0.98 },
          { id: "c2", type: "timeline", label: "Event Seq #15: Tower Handshake (00:14)", confidence: 0.94 },
        ],
        evidence_refs: ["EV-104", "EV-112"],
        confidence: 0.91,
        handoff: {
          targetAgentId: "geoscope",
          reason: "Communication blackout identified. Cell tower handshakes suggest physical displacement during the dormant period.",
        },
      };

    case "geoscope":
      return {
        content: `Location intelligence analysis completed for "${userPrompt}".

Extracted GPS coordinates and cell tower handshakes establish two co-location waypoints between the subject and secondary persons of interest in the Chennai Guindy industrial sector.`,
        toolExecutions: [
          { id: "t1", tool: "EXIF Geolocation", label: "Extracting GPS latitude/longitude from image evidence", status: "completed" },
          { id: "t2", tool: "Cell Tower Mapping", label: "Mapping tower azimuths & coverage sectors", status: "completed" },
          { id: "t3", tool: "Co-location Analysis", label: "Calculating spatial proximity within 50m radius", status: "completed" },
        ],
        findings: [
          {
            id: `find-${now}-3`,
            title: "Co-Location Rendezvous: Sector 4 (Guindy)",
            description: "Concurrent cell tower attachment by Suspect A and Suspect B devices within a 350-meter radius over 42 minutes.",
            confidence: 0.89,
            evidenceRefs: ["EV-112", "EV-143"],
            agentId: "geoscope",
            status: "verified",
          },
        ],
        citations: [
          { id: "c1", type: "evidence", label: "EV-112 (CDR Geolocation Dump)", source_id: "EV-112", confidence: 0.91 },
        ],
        evidence_refs: ["EV-112", "EV-143"],
        confidence: 0.89,
        handoff: {
          targetAgentId: "testimony",
          reason: "Geospatial data places subject at Guindy Sector 4 at 23:10 IST, directly conflicting with their alibi statement.",
        },
      };

    case "testimony":
      return {
        content: `Cross-examination of witness & suspect statements for "${userPrompt}" complete.

Cross-verification flagged a critical contradiction between Statement #2 (claiming subject was at home) and forensic digital location logs placing the subject 14km away at the relevant hour.`,
        toolExecutions: [
          { id: "t1", tool: "Claim Extraction", label: "Extracting verifiable factual assertions from statements", status: "completed" },
          { id: "t2", tool: "Cross-Evidence Verifier", label: "Verifying asserted alibis against digital forensics", status: "completed" },
          { id: "t3", tool: "Contradiction Flagging", label: "Detecting temporal and spatial contradictions", status: "completed" },
        ],
        findings: [
          {
            id: `find-${now}-4`,
            title: "Alibi Contradiction: Home Whereabouts Claim",
            description: "Subject swore they remained at residence after 21:00. Forensic cell telemetry verifies movement across 3 sectors between 22:30 and 23:45.",
            confidence: 0.96,
            evidenceRefs: ["EV-042", "EV-112"],
            agentId: "testimony",
            status: "verified",
          },
        ],
        citations: [
          { id: "c1", type: "evidence", label: "EV-042 (Affidavit Transcript #2)", source_id: "EV-042", confidence: 0.99 },
          { id: "c2", type: "evidence", label: "EV-112 (CDR Telemetry)", source_id: "EV-112", confidence: 0.96 },
        ],
        evidence_refs: ["EV-042", "EV-112"],
        confidence: 0.96,
        handoff: {
          targetAgentId: "evidence-review",
          reason: "Contradiction confirmed. Evidence Review Agent should audit the cryptographic custody and admissibility of EV-112.",
        },
      };

    case "evidence-review":
      return {
        content: `Forensic integrity and Chain of Custody audit completed for "${userPrompt}".

All 14 active evidence records in Case ${cId} were audited. Cryptographic SHA-256 hashes match ingestion anchors with zero bit-level corruption. One evidence item is missing a secondary transfer custody counter-signature.`,
        toolExecutions: [
          { id: "t1", tool: "SHA-256 Integrity Check", label: "Re-computing disk SHA-256 vs database anchors", status: "completed" },
          { id: "t2", tool: "Custody Audit", label: "Verifying actor signatures and timestamp lineage", status: "completed" },
          { id: "t3", tool: "Admissibility Checklist", label: "Evaluating conformance with Section 65B criteria", status: "completed" },
        ],
        findings: [
          {
            id: `find-${now}-5`,
            title: "Chain of Custody Notice: Minor Handoff Gap on EV-112",
            description: "Physical evidence drive transfer from Lab Vault to Analysis Workstation lacks secondary witness counter-signature. Hash remains 100% intact.",
            confidence: 0.98,
            evidenceRefs: ["EV-112"],
            agentId: "evidence-review",
            status: "needs-review",
          },
        ],
        citations: [
          { id: "c1", type: "evidence", label: "EV-112 SHA-256: 4a2b9c7d8e...", source_id: "EV-112", confidence: 1.0 },
        ],
        evidence_refs: ["EV-112"],
        confidence: 0.98,
        handoff: {
          targetAgentId: "report",
          reason: "Evidence verification complete. Ready to compile a court-admissible forensic exhibit catalog.",
        },
      };

    case "report":
      return {
        content: `Preliminary forensic synthesis compiled for "${userPrompt}".

Synthesized findings across 7 investigation domains:
- 1 Verified Entity Linkage (Rahul Kumar ↔ +91 9876543210)
- 1 Unverified Communication Blackout (90 minutes)
- 1 Verified Co-Location Event (Guindy Sector 4)
- 1 Factual Alibi Contradiction against digital telemetry
- 100% Cryptographic Hash Verification across all 14 evidence exhibits.`,
        toolExecutions: [
          { id: "t1", tool: "Findings Aggregator", label: "Compiling findings across all specialist agents", status: "completed" },
          { id: "t2", tool: "Citation Indexer", label: "Cross-referencing evidence hash catalog", status: "completed" },
          { id: "t3", tool: "Court Exhibit Formatter", label: "Formatting legal executive summary", status: "completed" },
        ],
        findings: [
          {
            id: `find-${now}-6`,
            title: "Executive Synthesis: Cyber Fraud Investigation Complete",
            description: "Corroborated digital footprint contradicts subject's sworn testimony with 95% aggregate forensic confidence.",
            confidence: 0.95,
            evidenceRefs: ["EV-042", "EV-087", "EV-104", "EV-112"],
            agentId: "report",
            status: "verified",
          },
        ],
        citations: [
          { id: "c1", type: "report", label: "Forensic Case Exhibit CK-2026-021-FINAL", confidence: 0.97 },
        ],
        evidence_refs: ["EV-042", "EV-087", "EV-104", "EV-112"],
        confidence: 0.95,
      };

    case "case-orchestrator":
    default:
      return {
        content: `Case Orchestrator review for "${userPrompt}":

I've evaluated the case posture across all investigation dimensions. The investigation currently holds 14 evidence files, 38 extracted entities, and 27 timeline events.

Next recommended step: Delegate deep link analysis to Detective Agent, followed by temporal reconstruction via Timeline Agent.`,
        toolExecutions: [
          { id: "t1", tool: "Case Posture Evaluation", label: `Auditing Case ${cId} evidence and findings`, status: "completed" },
          { id: "t2", tool: "Agent Delegation Matrix", label: "Determining optimal specialist routing", status: "completed" },
          { id: "t3", tool: "Gap Analysis", label: "Identifying missing investigative leads", status: "completed" },
        ],
        findings: [
          {
            id: `find-${now}-0`,
            title: "Lead Prioritization: Financial & Telemetry Links",
            description: "Primary focus recommended on cross-referencing phone extraction logs with recent bank transactions.",
            confidence: 0.92,
            evidenceRefs: ["EV-087"],
            agentId: "case-orchestrator",
            status: "verified",
          },
        ],
        citations: [
          { id: "c1", type: "processing", label: "Case Status: Active (14 Evidence, 38 Entities)", confidence: 1.0 },
        ],
        evidence_refs: ["EV-087"],
        confidence: 0.92,
        handoff: {
          targetAgentId: "detective",
          reason: "Proceed with deep entity and communication network discovery.",
        },
      };
  }
}
