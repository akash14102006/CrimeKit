import type { RoleName } from "@/types/auth";

export type { RoleName };

/** Canonical backend roles. */
export const ROLES: readonly RoleName[] = [
  "admin",
  "investigator",
  "analyst",
  "evidence_officer",
  "compliance_officer",
  "auditor",
  "viewer",
  "demo_evaluator",
  "jury_evaluator",
] as const;

/** Legacy role name accepted for backward compatibility. */
export const LEGACY_USER_ROLE = "user";

export type RoleWithLegacy = RoleName | typeof LEGACY_USER_ROLE;

/** Role -> label mapping for UI presentation. */
export const ROLE_LABELS: Record<RoleWithLegacy, string> = {
  admin: "Administrator",
  investigator: "Investigator",
  analyst: "Analyst",
  evidence_officer: "Evidence Officer",
  compliance_officer: "Compliance Officer",
  auditor: "Auditor",
  viewer: "Viewer",
  demo_evaluator: "Demo Evaluator",
  jury_evaluator: "Jury Evaluator",
  user: "User",
};

/** Canonical permission set understood by the frontend. */
export const PERMISSIONS = [
  "case:create",
  "case:read",
  "case:update",
  "case:delete",
  "evidence:upload",
  "evidence:read",
  "evidence:update",
  "evidence:delete",
  "kg:query",
  "timeline:read",
  "search:query",
  "compliance:manage",
  "audit:read",
  "user:manage",
  "analytics:read",
] as const;

export type PermissionName = (typeof PERMISSIONS)[number];

/**
 * Role -> permission matrix. Mirrors the backend permission configuration so
 * the frontend can gate UI affordances without additional round trips.
 */
export const ROLE_PERMISSIONS: Record<RoleName, readonly PermissionName[]> = {
  admin: [...PERMISSIONS],
  investigator: [
    "case:create",
    "case:read",
    "case:update",
    "case:delete",
    "evidence:upload",
    "evidence:read",
    "evidence:update",
    "evidence:delete",
    "kg:query",
    "timeline:read",
    "search:query",
  ],
  jury_evaluator: [
    "case:create",
    "case:read",
    "case:update",
    "case:delete",
    "evidence:upload",
    "evidence:read",
    "evidence:update",
    "evidence:delete",
    "kg:query",
    "timeline:read",
    "search:query",
    "compliance:manage",
    "audit:read",
    "analytics:read",
  ],
  demo_evaluator: [
    "case:create",
    "case:read",
    "case:update",
    "case:delete",
    "evidence:upload",
    "evidence:read",
    "evidence:update",
    "evidence:delete",
    "kg:query",
    "timeline:read",
    "search:query",
    "compliance:manage",
    "audit:read",
    "analytics:read",
  ],

  analyst: [
    "case:read",
    "evidence:read",
    "kg:query",
    "timeline:read",
    "search:query",
    "analytics:read",
  ],
  evidence_officer: [
    "case:read",
    "evidence:upload",
    "evidence:read",
    "evidence:update",
    "timeline:read",
  ],
  compliance_officer: [
    "case:read",
    "evidence:read",
    "compliance:manage",
    "audit:read",
    "timeline:read",
  ],
  auditor: ["case:read", "evidence:read", "audit:read", "timeline:read"],
  viewer: ["case:read", "evidence:read", "timeline:read"],
};

/** Derived role used by legacy code that expects a single primary role. */
export function primaryRole(
  roles: readonly string[] | undefined,
  role: string | undefined,
): RoleName | string {
  if (roles && roles.length > 0) {
    const canonical = roles.find((r): r is RoleName =>
      (ROLES as readonly string[]).includes(r),
    );
    if (canonical) return canonical;
    return roles[0];
  }
  return role ?? LEGACY_USER_ROLE;
}
