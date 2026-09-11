"use client";

import { useMemo } from "react";
import { Shield, Users } from "lucide-react";
import { useAdminUsers } from "../hooks/useAdmin";
import { ROLES, ROLE_LABELS, ROLE_PERMISSIONS } from "@/constants/roles";

export function RoleManagementPanel() {
  const { data: users, isLoading } = useAdminUsers();

  const roleStats = useMemo(() => {
    if (!users) return [];
    return ROLES.map((role) => {
      const assigned = users.filter((u) => u.roles.includes(role)).length;
      const permissions = ROLE_PERMISSIONS[role] ?? [];
      return {
        role,
        label: ROLE_LABELS[role],
        assigned,
        permissionCount: permissions.length,
        isSystem: role === "admin" || role === "viewer",
      };
    });
  }, [users]);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-20 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Shield className="h-5 w-5" />
        <h2 className="text-lg font-semibold">Role Management</h2>
        <span className="text-sm text-muted-foreground">
          ({roleStats.length} roles)
        </span>
      </div>

      <div className="space-y-2">
        {roleStats.map(({ role, label, assigned, permissionCount, isSystem }) => (
          <div
            key={role}
            className="flex items-center gap-4 rounded-lg border bg-card p-4"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <Shield className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium">{label}</p>
                {isSystem && (
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                    System
                  </span>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                {permissionCount} permissions
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">{assigned}</span>
              <span className="text-muted-foreground">users</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
