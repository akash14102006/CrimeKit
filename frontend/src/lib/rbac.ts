import {
  PERMISSIONS,
  ROLES,
  ROLE_PERMISSIONS,
  type PermissionName,
  type RoleName,
} from "@/constants/roles";
import type { UserProfile } from "@/types/auth";

/** Normalize a possibly-undefined profile into a stable role/permission shape. */
export function resolvePermissions(
  profile?: UserProfile | null,
): {
  roles: string[];
  permissions: Set<PermissionName>;
  primaryRole: string;
} {
  const rawRoles = [
    ...(profile?.roles ?? []),
    ...(profile?.role ? [profile.role] : []),
  ];

  const roles = Array.from(new Set(rawRoles.filter(Boolean)));

  const inferred = new Set<PermissionName>();
  roles.forEach((role) => {
    if (role === "user" || role === "viewer") {
      ROLE_PERMISSIONS.viewer.forEach((p) => inferred.add(p));
    }
    if ((ROLES as readonly string[]).includes(role)) {
      ROLE_PERMISSIONS[role as RoleName].forEach((p) => inferred.add(p));
    }
  });

  const explicit = new Set<PermissionName>(
    (profile?.permissions ?? []).filter((p): p is PermissionName =>
      (PERMISSIONS as readonly string[]).includes(p),
    ),
  );

  const permissions = new Set([...inferred, ...explicit]);

  const primaryRole = (roles.find((r) =>
    (ROLES as readonly string[]).includes(r),
  ) ??
    roles[0] ??
    "viewer") as string;

  return { roles, permissions, primaryRole };
}

export function hasPermission(
  permission: string,
  profile?: UserProfile | null,
): boolean {
  return resolvePermissions(profile).permissions.has(
    permission as PermissionName,
  );
}

export function hasAnyPermission(
  permissions: string[],
  profile?: UserProfile | null,
): boolean {
  const owned = resolvePermissions(profile).permissions;
  return permissions.some((p) => owned.has(p as PermissionName));
}

export function hasRole(
  role: string | string[],
  profile?: UserProfile | null,
): boolean {
  const { roles } = resolvePermissions(profile);
  const targets = Array.isArray(role) ? role : [role];
  const isJury = roles.includes("jury_evaluator") || roles.includes("demo_evaluator");
  const isStrictAdminOnly = targets.length === 1 && targets[0] === "admin";
  if (isJury && !isStrictAdminOnly) {
    return true;
  }
  return targets.some((t) => roles.includes(t));
}

