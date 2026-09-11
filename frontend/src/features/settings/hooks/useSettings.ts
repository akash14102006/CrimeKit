import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "@/components/ui/toast";
import { settingsService } from "../services/settingsService";
import { getErrorMessage } from "@/lib/api-client";

export function useUserProfile() {
  return useQuery({
    queryKey: ["settings", "profile"],
    queryFn: settingsService.me,
    staleTime: 60_000,
  });
}

export function useApiKeys() {
  return useQuery({
    queryKey: ["settings", "api-keys"],
    queryFn: settingsService.listApiKeys,
    staleTime: 30_000,
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ["settings", "health"],
    queryFn: settingsService.healthDetailed,
    staleTime: 30_000,
  });
}

export function useAuditVerify() {
  return useQuery({
    queryKey: ["settings", "audit-verify"],
    queryFn: settingsService.verifyAuditChain,
    staleTime: 60_000,
  });
}

export function useCreateApiKey() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      name,
      environment,
      scopes,
    }: {
      name: string;
      environment?: string;
      scopes?: string[];
    }) => settingsService.createApiKey(name, environment, scopes),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["settings", "api-keys"] });
      toast.add({
        title: "API Key Created",
        description: `Key: ${data.raw_key}`,
        type: "success",
      });
    },
    onError: (err: unknown) => {
      toast.add({
        title: "Failed to Create API Key",
        description: getErrorMessage(err),
        type: "error",
      });
    },
  });
}

export function useRevokeApiKey() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (keyId: string) => settingsService.revokeApiKey(keyId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["settings", "api-keys"] });
      toast.add({ title: "API Key Revoked", type: "success" });
    },
    onError: (err: unknown) => {
      toast.add({
        title: "Failed to Revoke API Key",
        description: getErrorMessage(err),
        type: "error",
      });
    },
  });
}

export function useRotateApiKey() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (keyId: string) => settingsService.rotateApiKey(keyId),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["settings", "api-keys"] });
      toast.add({
        title: "API Key Rotated",
        description: `New key: ${data.raw_key}`,
        type: "success",
      });
    },
    onError: (err: unknown) => {
      toast.add({
        title: "Failed to Rotate API Key",
        description: getErrorMessage(err),
        type: "error",
      });
    },
  });
}
