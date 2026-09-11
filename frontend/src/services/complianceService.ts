import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import {
  ComplianceReport,
  ComplianceReportGenerateRequest,
  ComplianceReportType,
  DataClassification,
  DataClassificationRequest,
  ExportCaseRequest,
  ExportEvidenceRequest,
  ExportResponse,
  GDPRDeleteRequest,
  GDPRStatusResponse,
  LegalHold,
  LegalHoldCreateRequest,
  LegalHoldReleaseResponse,
  LegalHoldsResponse,
  RetentionExecuteResponse,
  RetentionPoliciesResponse,
  RetentionPolicy,
  RetentionPolicyCreateRequest,
  RetentionPolicyUpdateRequest,
} from "@/types/compliance";

export const complianceService = {
  gdprDelete: (payload: GDPRDeleteRequest): Promise<unknown> =>
    api.post<unknown>(API.compliance.gdprDelete, payload),

  gdprStatus: (userId: string): Promise<GDPRStatusResponse> =>
    api.get<GDPRStatusResponse>(API.compliance.gdprStatus(userId)),

  retentionPolicies: (): Promise<RetentionPoliciesResponse> =>
    api.get<RetentionPoliciesResponse>(API.compliance.retentionPolicies),

  createRetentionPolicy: (
    payload: RetentionPolicyCreateRequest,
  ): Promise<RetentionPolicy> =>
    api.post<RetentionPolicy>(API.compliance.retentionPolicies, payload),

  updateRetentionPolicy: (
    policyId: string,
    payload: RetentionPolicyUpdateRequest,
  ): Promise<RetentionPolicy> =>
    api.put<RetentionPolicy>(
      API.compliance.retentionPolicy(policyId),
      payload,
    ),

  deleteRetentionPolicy: (policyId: string): Promise<{ detail: string }> =>
    api.delete<{ detail: string }>(
      API.compliance.retentionPolicy(policyId),
    ),

  executeRetention: (): Promise<RetentionExecuteResponse> =>
    api.post<RetentionExecuteResponse>(API.compliance.retentionExecute),

  legalHolds: (): Promise<LegalHoldsResponse> =>
    api.get<LegalHoldsResponse>(API.compliance.legalHold),

  placeLegalHold: (payload: LegalHoldCreateRequest): Promise<LegalHold> =>
    api.post<LegalHold>(API.compliance.legalHold, payload),

  releaseLegalHold: (holdId: string): Promise<LegalHoldReleaseResponse> =>
    api.delete<LegalHoldReleaseResponse>(API.compliance.legalHoldItem(holdId)),

  checkLegalHold: (
    entityType: "case" | "evidence",
    entityId: string,
  ): Promise<unknown> =>
    api.get<unknown>(
      API.compliance.legalHoldCheck(entityType, entityId),
    ),

  generateReport: (
    payload: ComplianceReportGenerateRequest,
  ): Promise<ComplianceReport> =>
    api.post<ComplianceReport>(API.compliance.reportsGenerate, payload),

  reports: (): Promise<{ reports: ComplianceReport[]; total: number }> =>
    api.get<{ reports: ComplianceReport[]; total: number }>(
      API.compliance.reports,
    ),

  classify: (payload: DataClassificationRequest): Promise<DataClassification> =>
    api.post<DataClassification>(API.compliance.classification, payload),

  verifyChain: (): Promise<unknown> =>
    api.get<unknown>(API.compliance.verifyChain),

  exportEvidence: (
    evidenceId: string,
    params: ExportEvidenceRequest,
  ): Promise<ExportResponse> =>
    api.post<ExportResponse>(
      `${API.compliance.exportEvidence(evidenceId)}?${new URLSearchParams(
        params as Record<string, string>,
      )}`,
    ),

  exportCase: (
    caseId: string,
    params: ExportCaseRequest,
  ): Promise<ExportResponse> =>
    api.post<ExportResponse>(
      `${API.compliance.exportCase(caseId)}?${new URLSearchParams(
        params as Record<string, string>,
      )}`,
    ),
};

export type { ComplianceReportType };
