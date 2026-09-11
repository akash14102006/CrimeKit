import type { Dict, ID, ISOString, Nullable } from "./common";
import type { CaseSummary } from "./case";

export interface WorkspaceEvidenceItem {
  id: ID;
  filename: string;
  sha256: string;
  size: number;
  mime_type?: Nullable<string>;
  uploaded_by?: Nullable<string>;
  uploaded_at?: Nullable<ISOString>;
  custody_entries?: number;
  has_document?: boolean;
  ai_score?: Nullable<number>;
}

export interface WorkspaceCustodyEvent {
  id: ID;
  evidence_id: string;
  action: string;
  actor_id?: Nullable<string>;
  timestamp?: Nullable<ISOString>;
  notes?: Nullable<string>;
}

export interface WorkspaceTimelineEvent {
  source_type: string;
  source_id?: Nullable<string>;
  timestamp?: Nullable<ISOString>;
  date?: Nullable<string>;
  summary: string;
}

export interface WorkspaceKGSummary {
  available: boolean;
  status: string;
  source?: string;
  entity_count?: number;
  relationship_count?: number;
  timeline_event_count?: number;
  entities?: Dict[];
  timeline_events?: Dict[];
  notes?: string[];
}

export interface WorkspaceAIFinding {
  document_id: string;
  evidence_id?: Nullable<string>;
  score: number;
  snippet?: Nullable<string>;
}

export interface WorkspaceRelatedEvidence {
  evidence_id: string;
  related_evidence_id: string;
  similarity: number;
  reason: string;
}

export interface WorkspaceSimilarCase {
  case_id: string;
  title: string;
  similarity: number;
  reason: string;
}

export interface WorkspaceProgress {
  evidence_total: number;
  evidence_with_custody: number;
  evidence_with_documents: number;
  forensic_jobs_total: number;
  forensic_jobs_completed: number;
  forensic_jobs_failed: number;
  completion_percent: number;
}

export interface WorkspaceRiskIndicator {
  code: string;
  severity: "low" | "medium" | "high";
  message: string;
  details?: Dict;
}

export interface CourtReportStatus {
  status: "draft" | "review" | "ready" | "blocked";
  completion_percent: number;
  blockers?: string[];
  notes?: string[];
}

export interface InvestigationWorkspace {
  case: CaseSummary;
  evidence: WorkspaceEvidenceItem[];
  custody: WorkspaceCustodyEvent[];
  timeline: WorkspaceTimelineEvent[];
  knowledge_graph: WorkspaceKGSummary;
  ai_findings: WorkspaceAIFinding[];
  related_evidence: WorkspaceRelatedEvidence[];
  similar_cases: WorkspaceSimilarCase[];
  progress: WorkspaceProgress;
  risk_indicators: WorkspaceRiskIndicator[];
  court_report: CourtReportStatus;
  generated_at: ISOString;
}


