import type { RoleName } from "@/types/auth";

export type AdminTab =
  | "overview"
  | "users"
  | "roles"
  | "permissions"
  | "organizations"
  | "projects"
  | "api-keys"
  | "mfa"
  | "audit";

export interface AdminSecurityStats {
  totalUsers: number;
  activeUsers: number;
  totalOrganizations: number;
  totalProjects: number;
  totalApiKeys: number;
  activeApiKeys: number;
  rolesBreakdown: Record<string, number>;
  auditChainValid: boolean;
}

export interface PermissionMatrixRow {
  role: RoleName;
  permissions: string[];
}

export interface AdminUser {
  id: string;
  email: string;
  roles: string[];
  is_active: boolean;
  created_at?: string;
}
