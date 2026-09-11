import type { ID, ISOString, Nullable } from "./common";

export type ReportType =
  | "court_ready"
  | "executive_summary"
  | "technical_forensic"
  | "evidence_report"
  | "chain_of_custody"
  | "audit_report"
  | "compliance_report"
  | "investigation_summary"
  | "timeline_report"
  | "processing_report"
  | "kg_report"
  | "ai_summary"
  | string;

export type ReportStatus =
  | "generated"
  | "pending"
  | "generating"
  | "queued"
  | "failed"
  | "cancelled"
  | string;

export interface Report {
  id: ID;
  case_id: ID;
  title: string;
  report_type: ReportType;
  status: ReportStatus;
  content_markdown: string;
  created_by: string;
  created_at: ISOString;
  updated_at?: Nullable<ISOString>;
  file_path?: Nullable<string>;
  file_size?: Nullable<number>;
  format?: Nullable<string>;
}

export interface ReportCreateRequest {
  case_id: string;
  title: string;
  report_type?: ReportType;
  notes?: string;
}

export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  report_type: ReportType;
  icon: string;
  sections: string[];
  backendGenerated: boolean;
}

export interface ReportHistoryEntry {
  id: ID;
  case_id: ID;
  case_title?: string;
  title: string;
  report_type: ReportType;
  status: ReportStatus;
  created_by: string;
  created_at: ISOString;
  format?: Nullable<string>;
  file_size?: Nullable<number>;
  version?: number;
}

export interface ReportDownloadOptions {
  format: "pdf" | "docx" | "json" | "zip";
  includeEvidence?: boolean;
  includeAuditTrail?: boolean;
  includeChainOfCustody?: boolean;
}

export interface AuditLogEntry {
  id: ID;
  action: string;
  entity_type?: Nullable<string>;
  entity_id?: Nullable<string>;
  actor_id?: Nullable<string>;
  actor_email?: Nullable<string>;
  details?: Nullable<Record<string, unknown>>;
  created_at?: Nullable<ISOString>;
}

export const REPORT_TEMPLATES: ReportTemplate[] = [
  {
    id: "court_ready",
    name: "Court Report",
    description: "Legally admissible court-ready forensic report with chain of custody",
    report_type: "court_ready",
    icon: "Scale",
    sections: ["Executive Summary", "Evidence Inventory", "Chain of Custody", "Audit Affirmation"],
    backendGenerated: true,
  },
  {
    id: "evidence_report",
    name: "Evidence Report",
    description: "Detailed forensic evidence analysis report",
    report_type: "evidence_report",
    icon: "FileText",
    sections: ["Evidence Details", "Hash Verification", "Metadata", "OCR Results", "AI Analysis"],
    backendGenerated: true,
  },
  {
    id: "chain_of_custody",
    name: "Chain of Custody",
    description: "Complete chain of custody documentation",
    report_type: "chain_of_custody",
    icon: "Link",
    sections: ["Transfer History", "Owner History", "Integrity Verification", "Audit Trail"],
    backendGenerated: true,
  },
  {
    id: "audit_report",
    name: "Audit Report",
    description: "System audit trail and access log report",
    report_type: "audit_report",
    icon: "Shield",
    sections: ["Authentication Events", "User Actions", "Evidence Access", "Processing Jobs"],
    backendGenerated: true,
  },
  {
    id: "executive_summary",
    name: "Executive Summary",
    description: "High-level investigation summary for stakeholders",
    report_type: "executive_summary",
    icon: "FileBarChart",
    sections: ["Case Overview", "Key Findings", "Timeline", "Recommendations"],
    backendGenerated: true,
  },
  {
    id: "compliance_report",
    name: "Compliance Report",
    description: "Regulatory compliance documentation (GDPR, ISO27001, SOC2)",
    report_type: "compliance_report",
    icon: "CheckSquare",
    sections: ["Compliance Status", "Policy Adherence", "Data Classification", "Retention"],
    backendGenerated: true,
  },
  {
    id: "investigation_summary",
    name: "Investigation Summary",
    description: "Comprehensive investigation overview with AI insights",
    report_type: "investigation_summary",
    icon: "Search",
    sections: ["Case Details", "Evidence Summary", "Entity Analysis", "AI Findings", "Timeline"],
    backendGenerated: true,
  },
  {
    id: "timeline_report",
    name: "Timeline Report",
    description: "Chronological timeline of investigation events",
    report_type: "timeline_report",
    icon: "CalendarClock",
    sections: ["Timeline Events", "Entity Activity", "Evidence Activity", "Analysis"],
    backendGenerated: true,
  },
  {
    id: "kg_report",
    name: "Knowledge Graph Report",
    description: "Entity relationship and knowledge graph analysis",
    report_type: "kg_report",
    icon: "Workflow",
    sections: ["Entity Map", "Relationships", "Clusters", "Insights"],
    backendGenerated: true,
  },
  {
    id: "processing_report",
    name: "Processing Report",
    description: "Forensic processing results and pipeline status",
    report_type: "processing_report",
    icon: "Cpu",
    sections: ["Processing Status", "Processor Results", "Errors", "Timeline"],
    backendGenerated: true,
  },
];
