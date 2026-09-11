import React from "react";
import { useAuthStore } from "@/store/authStore";
import { hasRole } from "@/lib/rbac";

export interface RoleGateProps {
  children: React.ReactNode;
  allowedRoles: string[];
  fallback?: React.ReactNode;
}

export function RoleGate({ children, allowedRoles, fallback = null }: RoleGateProps) {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return <>{fallback}</>;
  }

  if (!hasRole(allowedRoles, user)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
