import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { caseService, type CaseListParams } from "@/services/caseService";
import type { CaseCreate, CaseListResponse, CaseOut, CaseUpdate } from "@/types/case";
import { useAuthStore } from "@/store/authStore";

export function useCases(params?: CaseListParams) {
  const { isAuthenticated, sessionToken } = useAuthStore();
  return useQuery({
    queryKey: ["cases", params],
    queryFn: () => caseService.list(params),
    enabled: isAuthenticated && !!sessionToken,
  });
}

export function useCase(id?: string) {
  const { isAuthenticated, sessionToken } = useAuthStore();
  return useQuery({
    queryKey: ["cases", id],
    queryFn: () => caseService.detail(id as string),
    enabled: !!id && isAuthenticated && !!sessionToken,
  });
}

export function useCreateCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CaseCreate) => caseService.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cases"] }),
  });
}

export function useUpdateCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: CaseUpdate }) =>
      caseService.update(id, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["cases"] });
      queryClient.invalidateQueries({ queryKey: ["cases", variables.id] });
    },
  });
}

export function usePatchCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<CaseUpdate> }) =>
      caseService.patch(id, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["cases"] });
      queryClient.invalidateQueries({ queryKey: ["cases", variables.id] });
    },
  });
}

export function useAssignCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, userId }: { id: string; userId: string | null }) =>
      caseService.assign(id, userId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["cases"] });
      queryClient.invalidateQueries({ queryKey: ["cases", variables.id] });
    },
  });
}

export function useDeleteCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => caseService.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cases"] }),
  });
}

export type { CaseOut, CaseCreate, CaseUpdate, CaseListResponse, CaseListParams };
