import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import type { RoleUser } from "@/services/rolesService";

export interface ApiKeyRecord {
  id: string;
  name: string;
  key_prefix: string;
  environment: string;
  is_active: boolean;
  created_at: string;
  last_used_at: string | null;
  expires_at: string | null;
  scopes: string[] | null;
}

export interface ApiKeyCreatedResponse extends ApiKeyRecord {
  raw_key: string;
}

export interface OrganizationRecord {
  id: string;
  name: string;
  description: string | null;
  plan: string | null;
  created_at: string;
  is_active: boolean;
}

export interface OrganizationDetail extends OrganizationRecord {
  projects: number;
  members: number;
  storage_used: number;
  cases: number;
  evidence: number;
}

export interface OrganizationMember {
  user_id: string;
  role: string;
  joined_at: string;
}

export interface AuditVerifyResult {
  is_valid: boolean;
  chain_length: number;
  broken_at: string | null;
  verified_at: string;
}

export const adminService = {
  users: (): Promise<RoleUser[]> => api.get<RoleUser[]>(API.roles.users),

  assignRole: (email: string, role: string): Promise<{ email: string; roles: string[] }> =>
    api.post(API.roles.assign, { email, role }),

  revokeRole: (email: string, role: string): Promise<{ email: string; roles: string[] }> =>
    api.post(API.roles.revoke, { email, role }),

  listApiKeys: (): Promise<ApiKeyRecord[]> => api.get<ApiKeyRecord[]>(API.apiKeys.list),

  createApiKey: (name: string, environment = "live", scopes?: string[]): Promise<ApiKeyCreatedResponse> =>
    api.post<ApiKeyCreatedResponse>(API.apiKeys.create, { name, environment, scopes }),

  revokeApiKey: (keyId: string): Promise<{ detail: string }> =>
    api.delete<{ detail: string }>(API.apiKeys.revoke(keyId)),

  rotateApiKey: (keyId: string): Promise<ApiKeyCreatedResponse> =>
    api.post<ApiKeyCreatedResponse>(API.apiKeys.rotate(keyId)),

  listOrganizations: (): Promise<OrganizationRecord[]> =>
    api.get<OrganizationRecord[]>(API.tenants.organizations),

  getOrganization: (orgId: string): Promise<OrganizationDetail> =>
    api.get<OrganizationDetail>(API.tenants.organization(orgId)),

  listOrgMembers: (orgId: string): Promise<OrganizationMember[]> =>
    api.get<OrganizationMember[]>(API.tenants.members(orgId)),

  verifyAuditChain: (): Promise<AuditVerifyResult> =>
    api.get<AuditVerifyResult>(API.compliance.verifyChain),

  healthDetailed: (): Promise<Record<string, unknown>> =>
    api.get<Record<string, unknown>>(API.health.detailed),
};
