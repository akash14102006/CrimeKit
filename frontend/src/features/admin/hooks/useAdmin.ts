import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "@/components/ui/toast";
import { adminService } from "../services/adminService";
import { getErrorMessage } from "@/lib/api-client";

export function useAdminUsers() {
  return useQuery({
    queryKey: ["admin", "users"],
    queryFn: adminService.users,
    staleTime: 30_000,
  });
}

export function useAdminApiKeys() {
  return useQuery({
    queryKey: ["admin", "api-keys"],
    queryFn: adminService.listApiKeys,
    staleTime: 30_000,
  });
}

export function useAdminOrganizations() {
  return useQuery({
    queryKey: ["admin", "organizations"],
    queryFn: adminService.listOrganizations,
    staleTime: 30_000,
  });
}

export function useOrganizationDetail(orgId: string | null) {
  return useQuery({
    queryKey: ["admin", "organization", orgId],
    queryFn: () => adminService.getOrganization(orgId!),
    enabled: !!orgId,
    staleTime: 30_000,
  });
}

export function useOrganizationMembers(orgId: string | null) {
  return useQuery({
    queryKey: ["admin", "org-members", orgId],
    queryFn: () => adminService.listOrgMembers(orgId!),
    enabled: !!orgId,
    staleTime: 30_000,
  });
}

export function useAuditVerify() {
  return useQuery({
    queryKey: ["admin", "audit-verify"],
    queryFn: adminService.verifyAuditChain,
    staleTime: 60_000,
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ["admin", "health"],
    queryFn: adminService.healthDetailed,
    staleTime: 30_000,
  });
}

export function useAssignRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ email, role }: { email: string; role: string }) =>
      adminService.assignRole(email, role),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "users"] });
      toast.add({ title: "Role Assigned", type: "success" });
    },
    onError: (err: unknown) => {
      toast.add({
        title: "Failed to Assign Role",
        description: getErrorMessage(err),
        type: "error",
      });
    },
  });
}

export function useRevokeRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ email, role }: { email: string; role: string }) =>
      adminService.revokeRole(email, role),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "users"] });
      toast.add({ title: "Role Revoked", type: "success" });
    },
    onError: (err: unknown) => {
      toast.add({
        title: "Failed to Revoke Role",
        description: getErrorMessage(err),
        type: "error",
      });
    },
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
    }) => adminService.createApiKey(name, environment, scopes),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["admin", "api-keys"] });
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
    mutationFn: (keyId: string) => adminService.revokeApiKey(keyId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "api-keys"] });
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
    mutationFn: (keyId: string) => adminService.rotateApiKey(keyId),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["admin", "api-keys"] });
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
