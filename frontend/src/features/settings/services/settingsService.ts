import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  role?: string;
  roles?: string[];
  permissions?: string[];
  is_active?: boolean;
  organization?: string;
  tenant?: string;
}

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

export interface HealthStatus {
  status: string;
  database?: string;
  redis?: string;
  neo4j?: string;
  minio?: string;
  uptime?: string;
}

export const settingsService = {
  me: (): Promise<UserProfile> => api.get<UserProfile>(API.auth.me),

  listApiKeys: (): Promise<ApiKeyRecord[]> =>
    api.get<ApiKeyRecord[]>(API.apiKeys.list),

  createApiKey: (name: string, environment = "live", scopes?: string[]): Promise<ApiKeyCreatedResponse> =>
    api.post<ApiKeyCreatedResponse>(API.apiKeys.create, { name, environment, scopes }),

  revokeApiKey: (keyId: string): Promise<{ detail: string }> =>
    api.delete<{ detail: string }>(API.apiKeys.revoke(keyId)),

  rotateApiKey: (keyId: string): Promise<ApiKeyCreatedResponse> =>
    api.post<ApiKeyCreatedResponse>(API.apiKeys.rotate(keyId)),

  healthDetailed: (): Promise<HealthStatus> =>
    api.get<HealthStatus>(API.health.detailed),

  verifyAuditChain: (): Promise<{ is_valid: boolean; chain_length: number; verified_at: string }> =>
    api.get(API.compliance.verifyChain),
};
