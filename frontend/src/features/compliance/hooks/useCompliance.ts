"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { complianceService } from "@/services/complianceService";
import { useComplianceStore } from "../store/complianceStore";
import type {
  LegalHoldCreateRequest,
  RetentionPolicyCreateRequest,
  RetentionPolicyUpdateRequest,
  ComplianceReportGenerateRequest,
  ComplianceReportType,
} from "@/types/compliance";

export function useLegalHolds() {
  const { setLegalHolds } = useComplianceStore();

  return useQuery({
    queryKey: ["compliance", "legal-holds"],
    queryFn: async () => {
      const response = await complianceService.legalHolds();
      setLegalHolds(response.holds ?? []);
      return response;
    },
    staleTime: 30000,
  });
}

export function usePlaceLegalHold() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: LegalHoldCreateRequest) =>
      complianceService.placeLegalHold(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance", "legal-holds"] });
    },
  });
}

export function useReleaseLegalHold() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (holdId: string) => complianceService.releaseLegalHold(holdId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance", "legal-holds"] });
    },
  });
}

export function useRetentionPolicies() {
  const { setRetentionPolicies } = useComplianceStore();

  return useQuery({
    queryKey: ["compliance", "retention-policies"],
    queryFn: async () => {
      const response = await complianceService.retentionPolicies();
      setRetentionPolicies(response.policies ?? []);
      return response;
    },
    staleTime: 30000,
  });
}

export function useCreateRetentionPolicy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: RetentionPolicyCreateRequest) =>
      complianceService.createRetentionPolicy(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance", "retention-policies"] });
    },
  });
}

export function useUpdateRetentionPolicy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ policyId, payload }: { policyId: string; payload: RetentionPolicyUpdateRequest }) =>
      complianceService.updateRetentionPolicy(policyId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance", "retention-policies"] });
    },
  });
}

export function useDeleteRetentionPolicy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (policyId: string) => complianceService.deleteRetentionPolicy(policyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance", "retention-policies"] });
    },
  });
}

export function useExecuteRetention() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => complianceService.executeRetention(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance"] });
    },
  });
}

export function useComplianceReportsList() {
  const { setComplianceReports } = useComplianceStore();

  return useQuery({
    queryKey: ["compliance", "reports"],
    queryFn: async () => {
      const response = await complianceService.reports();
      setComplianceReports(response.reports ?? []);
      return response;
    },
    staleTime: 30000,
  });
}

export function useGenerateComplianceReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ComplianceReportGenerateRequest) =>
      complianceService.generateReport(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance", "reports"] });
    },
  });
}

export function useVerifyAuditChain() {
  return useQuery({
    queryKey: ["compliance", "audit-chain"],
    queryFn: () => complianceService.verifyChain(),
    staleTime: 60000,
  });
}

export function useExportEvidence() {
  return useMutation({
    mutationFn: ({
      evidenceId,
      format,
      purpose,
    }: {
      evidenceId: string;
      format: "csv" | "json" | "pdf_ready";
      purpose?: string;
    }) => complianceService.exportEvidence(evidenceId, { format, purpose }),
  });
}

export function useExportCase() {
  return useMutation({
    mutationFn: ({
      caseId,
      format,
      includesEvidence,
      includesAuditTrail,
      includesChainOfCustody,
    }: {
      caseId: string;
      format?: string;
      includesEvidence?: boolean;
      includesAuditTrail?: boolean;
      includesChainOfCustody?: boolean;
    }) =>
      complianceService.exportCase(caseId, {
        format,
        includes_evidence: includesEvidence,
        includes_audit_trail: includesAuditTrail,
        includes_chain_of_custody: includesChainOfCustody,
      }),
  });
}

export function useGDPRStatus(userId: string | null) {
  return useQuery({
    queryKey: ["compliance", "gdpr", userId],
    queryFn: () => complianceService.gdprStatus(userId!),
    enabled: !!userId,
    staleTime: 30000,
  });
}

export function useInitiateGDPRDeletion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, reason }: { userId: string; reason?: string }) =>
      complianceService.gdprDelete({ user_id: userId, reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance", "gdpr"] });
    },
  });
}
