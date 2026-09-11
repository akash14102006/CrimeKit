"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { reportService } from "@/services/reportService";
import { complianceService } from "@/services/complianceService";
import { useReportStore } from "../store/reportStore";
import type {
  Report,
  ReportCreateRequest,
  ReportDownloadOptions,
} from "@/types/report";
import type { ComplianceReportGenerateRequest, ComplianceReport } from "@/types/compliance";

export function useCaseReports(caseId: string | null) {
  const { setReports } = useReportStore();

  return useQuery({
    queryKey: ["reports", "case", caseId],
    queryFn: async () => {
      if (!caseId) return [];
      const reports = await reportService.byCase(caseId);
      setReports(reports);
      return reports;
    },
    enabled: !!caseId,
    staleTime: 30000,
  });
}

export function useReportDetail(reportId: string | null) {
  return useQuery({
    queryKey: ["reports", "detail", reportId],
    queryFn: () => reportService.detail(reportId!),
    enabled: !!reportId,
  });
}

export function useGenerateReport() {
  const queryClient = useQueryClient();
  const { setSelectedReport } = useReportStore();

  return useMutation({
    mutationFn: (payload: ReportCreateRequest) => reportService.create(payload),
    onSuccess: (report) => {
      setSelectedReport(report);
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });
}

export function useDeleteReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reportId: string) => reportService.delete(reportId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });
}

export function useExportReport() {
  return useMutation({
    mutationFn: async ({
      reportId,
      format,
    }: {
      reportId: string;
      format: "pdf" | "docx" | "json" | "zip";
    }) => {
      let blob: Blob;
      switch (format) {
        case "pdf":
          blob = await reportService.exportPdf(reportId);
          break;
        case "docx":
          blob = await reportService.exportDocx(reportId);
          break;
        case "json":
          blob = await reportService.exportJson(reportId);
          break;
        case "zip":
          blob = await reportService.exportZip(reportId);
          break;
        default:
          throw new Error(`Unsupported format: ${format}`);
      }
      return blob;
    },
  });
}

export function useComplianceReports() {
  const { setComplianceReports } = useReportStore();

  return useQuery({
    queryKey: ["compliance", "reports"],
    queryFn: async () => {
      const response = await complianceService.reports();
      setComplianceReports(response.reports);
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

export function useExportCase() {
  return useMutation({
    mutationFn: async ({
      caseId,
      options,
    }: {
      caseId: string;
      options: ReportDownloadOptions;
    }) => {
      const response = await complianceService.exportCase(caseId, {
        format: options.format,
        includes_evidence: options.includeEvidence,
        includes_audit_trail: options.includeAuditTrail,
        includes_chain_of_custody: options.includeChainOfCustody,
      });
      return response;
    },
  });
}

export function useExportEvidence() {
  return useMutation({
    mutationFn: async ({
      evidenceId,
      format,
    }: {
      evidenceId: string;
      format: "csv" | "json" | "pdf_ready";
    }) => {
      const response = await complianceService.exportEvidence(evidenceId, {
        format,
        purpose: "report_export",
      });
      return response;
    },
  });
}
