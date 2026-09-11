import type { Nullable } from "./common";

/** Canonical backend roles (mirrors backend permission matrix). */
export type RoleName =
  | "admin"
  | "investigator"
  | "analyst"
  | "evidence_officer"
  | "compliance_officer"
  | "auditor"
  | "viewer";

/** Legacy alias used by some client code paths. */
export type LegacyRoleName = "user";

export type Permission =
  | "case:create"
  | "case:read"
  | "case:update"
  | "case:delete"
  | "evidence:upload"
  | "evidence:read"
  | "evidence:update"
  | "evidence:delete"
  | "kg:query"
  | "timeline:read"
  | "search:query"
  | "compliance:manage"
  | "audit:read"
  | "user:manage"
  | "analytics:read";

export interface LoginRequest {
  email: string;
  password: string;
  /** Required only when the account has TOTP MFA enabled. */
  totp_code?: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  /** True when a second factor (TOTP) must be supplied before the token is usable. */
  mfa_required?: boolean;
}

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  role?: RoleName | LegacyRoleName;
  roles?: Array<RoleName | LegacyRoleName>;
  permissions?: Permission[];
  is_active?: boolean;
  organization?: string;
  tenant?: string;
}

export interface MFASecret {
  secret: string;
  provisioning_uri: string;
}

export interface RefreshRequest {
  token: string;
}

export interface LogoutRequest {
  token: string;
}

/** Persisted auth session snapshot used by the auth store. */
export interface AuthSession {
  accessToken: Nullable<string>;
  refreshToken: Nullable<string>;
  user: Nullable<UserProfile>;
}

export type AuthStatus = "unauthenticated" | "authenticated" | "mfa_required";
