import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workspaceService } from "@/services/workspaceService";
import type { InvestigationWorkspace } from "@/types/workspace";

export function useWorkspace(caseId?: string) {
  return useQuery({
    queryKey: ["workspace", caseId],
    queryFn: () => workspaceService.detail(caseId as string),
    enabled: !!caseId,
  });
}

export function useWorkspaceEvidence(caseId?: string) {
  return useQuery({
    queryKey: ["workspace", caseId, "evidence"],
    queryFn: () => workspaceService.evidence(caseId as string),
    enabled: !!caseId,
  });
}

export function useWorkspaceAIFindings(caseId?: string) {
  return useQuery({
    queryKey: ["workspace", caseId, "ai-findings"],
    queryFn: () => workspaceService.aiFindings(caseId as string),
    enabled: !!caseId,
  });
}

export function useWorkspaceRisks(caseId?: string) {
  return useQuery({
    queryKey: ["workspace", caseId, "risks"],
    queryFn: () => workspaceService.risks(caseId as string),
    enabled: !!caseId,
  });
}

export function useWorkspaceProgress(caseId?: string) {
  return useQuery({
    queryKey: ["workspace", caseId, "progress"],
    queryFn: () => workspaceService.progress(caseId as string),
    enabled: !!caseId,
  });
}

export function useWorkspaceCourtReport(caseId?: string) {
  return useQuery({
    queryKey: ["workspace", caseId, "court-report"],
    queryFn: () => workspaceService.courtReport(caseId as string),
    enabled: !!caseId,
  });
}

export function useWorkspaceCustody(caseId?: string) {
  return useQuery({
    queryKey: ["workspace", caseId, "custody"],
    queryFn: () => workspaceService.custody(caseId as string),
    enabled: !!caseId,
  });
}

export function useWorkspaceTimeline(caseId?: string) {
  return useQuery({
    queryKey: ["workspace", caseId, "timeline"],
    queryFn: () => workspaceService.timeline(caseId as string),
    enabled: !!caseId,
  });
}

export function useWorkspaceKGSummary(caseId?: string) {
  return useQuery({
    queryKey: ["workspace", caseId, "kg-summary"],
    queryFn: () => workspaceService.kgSummary(caseId as string),
    enabled: !!caseId,
  });
}

export function useWorkspaceMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (caseId: string) => workspaceService.detail(caseId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["workspace"] }),
  });
}

export type { InvestigationWorkspace };
