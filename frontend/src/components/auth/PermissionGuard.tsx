"use client";

import React from "react";
import { useRBAC } from "@/hooks/useRBAC";
import type { Permission } from "@/types/auth";

interface PermissionGuardProps {
  children: React.ReactNode;
  permission?: Permission;
  role?: string | string[];
  fallback?: React.ReactNode;
}

export function PermissionGuard({
  children,
  permission,
  role,
  fallback = null,
}: PermissionGuardProps) {
  const { hasPermission, hasRole } = useRBAC();

  if (permission && !hasPermission(permission)) {
    return <>{fallback}</>;
  }

  if (role && (Array.isArray(role) ? !role.some((r) => hasRole(r)) : !hasRole(role))) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
