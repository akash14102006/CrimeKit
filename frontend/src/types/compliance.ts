import type { ID, ISOString, Nullable } from "./common";

export interface GDPRDeleteRequest {
  user_id: string;
  reason?: Nullable<string>;
}

export interface GDPRRequestRecord {
  id: ID;
  status: string;
  reason: Nullable<string>;
  requested_at: Nullable<ISOString>;
  completed_at: Nullable<ISOString>;
  deleted_tables: unknown;
  denied_reason: Nullable<string>;
}

export interface GDPRStatusResponse {
  user_id: string;
  requests: GDPRRequestRecord[];
  total: number;
}

export interface RetentionPolicyCreateRequest {
  name: string;
  evidence_type?: string;
  case_status?: string;
  retention_days?: number;
  classification?: string;
  action_on_expiry?: string;
}

export interface RetentionPolicy {
  id: ID;
  name: string;
  description?: Nullable<string>;
  evidence_type?: Nullable<string>;
  case_status?: Nullable<string>;
  retention_days: number;
  classification: string;
  action_on_expiry: string;
  legal_hold_override?: boolean;
  is_active: boolean;
  created_at?: ISOString;
  updated_at?: Nullable<ISOString>;
}

export interface RetentionPoliciesResponse {
  policies: RetentionPolicy[];
  total: number;
}

export interface RetentionPolicyUpdateRequest {
  name?: string;
  evidence_type?: string;
  case_status?: string;
  retention_days?: number;
  classification?: string;
  action_on_expiry?: string;
  is_active?: boolean;
}

export interface RetentionExecuteResponse {
  run_id: ID;
  status: string;
  policies_evaluated: number;
  items_expired: number;
  items_archived: number;
  items_deleted: number;
  items_anonymized: number;
  started_at: Nullable<ISOString>;
  finished_at: Nullable<ISOString>;
}

export interface LegalHoldCreateRequest {
  case_id?: string;
  evidence_id?: string;
  reason: string;
  authority?: string;
}

export interface LegalHold {
  id: ID;
  case_id?: Nullable<string>;
  evidence_id?: Nullable<string>;
  reason: string;
  legal_reference?: Nullable<string>;
  status: string;
  placed_by?: Nullable<string>;
  placed_at?: Nullable<ISOString>;
  notes?: Nullable<string>;
}

export interface LegalHoldsResponse {
  holds: LegalHold[];
  total: number;
}

export interface LegalHoldReleaseResponse {
  id: ID;
  status: string;
  released_by?: Nullable<string>;
  released_at?: Nullable<ISOString>;
}

export type ComplianceReportType =
  | "gdpr"
  | "iso27001"
  | "soc2"
  | "retention"
  | "chain_of_custody";

export interface ComplianceReportGenerateRequest {
  report_type: ComplianceReportType | string;
  start_date?: Nullable<ISOString>;
  end_date?: Nullable<ISOString>;
  case_ids?: string[];
}

export interface ComplianceReport {
  id: ID;
  report_type: string;
  title: string;
  generated_by?: Nullable<string>;
  generated_at?: Nullable<ISOString>;
  period_start?: Nullable<ISOString>;
  period_end?: Nullable<ISOString>;
  content?: unknown;
}

export interface ComplianceReportsResponse {
  reports: ComplianceReport[];
  total: number;
}

export interface DataClassificationRequest {
  entity_type: string;
  entity_id: string;
  classification: string;
}

export interface DataClassification {
  id: ID;
  target_type?: string;
  target_id?: string;
  classification: string;
  classified_by?: Nullable<string>;
  classified_at?: Nullable<ISOString>;
  expires_at?: Nullable<ISOString>;
  notes?: Nullable<string>;
}

export interface ClassificationStatusResponse {
  target_type: string;
  target_id: string;
  classification: Nullable<string>;
  message?: string;
}

export interface ComplianceExportResponse {
  export_id: string;
  format: string;
}

export interface ExportEvidenceRequest {
  format?: "csv" | "json" | "pdf_ready";
  purpose?: string;
}

export interface ExportCaseRequest {
  format?: string;
  includes_evidence?: boolean;
  includes_audit_trail?: boolean;
  includes_chain_of_custody?: boolean;
}

export type ExportResponse = ComplianceExportResponse;

export interface ComplianceSummary {
  policies?: number;
  active_holds?: number;
  total?: number;
}
