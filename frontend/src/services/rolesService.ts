import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";

export interface RoleAssignRequest {
  email: string;
  role: string;
}

export interface RoleUser {
  id: string;
  email: string;
  roles: string[];
  is_active: boolean;
  created_at?: string;
}

export interface RoleAssignResponse {
  email: string;
  roles: string[];
}

export const rolesService = {
  assign: (payload: RoleAssignRequest): Promise<RoleAssignResponse> =>
    api.post<RoleAssignResponse>(API.roles.assign, payload),

  revoke: (payload: RoleAssignRequest): Promise<RoleAssignResponse> =>
    api.post<RoleAssignResponse>(API.roles.revoke, payload),

  users: (): Promise<RoleUser[]> => api.get<RoleUser[]>(API.roles.users),
};
