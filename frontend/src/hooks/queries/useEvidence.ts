import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { evidenceService, type EvidenceListParams } from "@/services/evidenceService";
import type {
  CustodyAppendRequest,
  Evidence,
  EvidenceListResponse,
  EvidenceUploadResponse,
} from "@/types/evidence";

export function useAllEvidence(params?: EvidenceListParams) {
  return useQuery({
    queryKey: ["evidence", params],
    queryFn: () => evidenceService.list(params),
  });
}

export function useEvidence(id?: string) {
  return useQuery({
    queryKey: ["evidence", id],
    queryFn: () => evidenceService.detail(id as string),
    enabled: !!id,
  });
}

export function useCaseEvidence(caseId?: string) {
  return useQuery({
    queryKey: ["evidence", "case", caseId],
    queryFn: () => evidenceService.byCase(caseId as string),
    enabled: !!caseId,
  });
}

export function useEvidenceCustody(evidenceId?: string) {
  return useQuery({
    queryKey: ["evidence", evidenceId, "custody"],
    queryFn: () => evidenceService.custodyStatus(evidenceId as string),
    enabled: !!evidenceId,
  });
}

export function useAppendCustody() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      evidenceId,
      payload,
    }: {
      evidenceId: string;
      payload: CustodyAppendRequest;
    }) => evidenceService.appendCustody(evidenceId, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["evidence", variables.evidenceId, "custody"],
      });
      queryClient.invalidateQueries({ queryKey: ["workspace"] });
    },
  });
}

export function useDeleteEvidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => evidenceService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
    },
  });
}

export function useReassignEvidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      evidenceId,
      caseId,
    }: {
      evidenceId: string;
      caseId: string | null;
    }) => evidenceService.reassign(evidenceId, caseId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      queryClient.invalidateQueries({ queryKey: ["evidence", variables.evidenceId] });
      queryClient.invalidateQueries({ queryKey: ["workspace"] });
    },
  });
}

export type { Evidence, EvidenceUploadResponse, EvidenceListResponse };
