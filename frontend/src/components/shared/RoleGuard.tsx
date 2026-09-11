"use client";

import { useAuthStore } from "@/store/authStore";
import { hasRole } from "@/lib/rbac";
import React from "react";

interface RoleGuardProps {
  children: React.ReactNode;
  allowedRoles: string[];
  fallback?: React.ReactNode;
}

/**
 * RoleGuard — Inline RBAC check for component-level visibility control.
 * Case-insensitive. Checks both user.role (primary) and user.roles[] (array).
 * Admin users always bypass role restrictions.
 */
export function RoleGuard({ children, allowedRoles, fallback = null }: RoleGuardProps) {
  const user = useAuthStore((state) => state.user);

  if (!user) return <>{fallback}</>;

  return <>{hasRole(allowedRoles, user) ? children : fallback}</>;
}
