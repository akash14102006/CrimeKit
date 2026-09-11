"use client";

import { useState, useMemo } from "react";
import {
  Users,
  Search,
  ChevronDown,
  ChevronRight,
  UserPlus,
  UserMinus,
} from "lucide-react";
import { useAdminUsers, useAssignRole, useRevokeRole } from "../hooks/useAdmin";
import { useAdminStore } from "../store/adminStore";
import { ROLES, ROLE_LABELS } from "@/constants/roles";
import type { RoleName } from "@/types/auth";

export function UserManagementPanel() {
  const { data: users, isLoading } = useAdminUsers();
  const assignRole = useAssignRole();
  const revokeRole = useRevokeRole();
  const { searchQuery, setSearchQuery, roleFilter, setRoleFilter } =
    useAdminStore();
  const [expandedUserId, setExpandedUserId] = useState<string | null>(null);

  const filteredUsers = useMemo(() => {
    if (!users) return [];
    return users.filter((u) => {
      const matchesSearch =
        !searchQuery ||
        u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        u.id.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesRole =
        !roleFilter || u.roles.includes(roleFilter);
      return matchesSearch && matchesRole;
    });
  }, [users, searchQuery, roleFilter]);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-16 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users className="h-5 w-5" />
          <h2 className="text-lg font-semibold">User Management</h2>
          <span className="text-sm text-muted-foreground">
            ({filteredUsers.length} users)
          </span>
        </div>
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search users by email or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border bg-background pl-9 pr-3 py-2 text-sm"
          />
        </div>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="rounded-lg border bg-background px-3 py-2 text-sm"
        >
          <option value="">All Roles</option>
          {ROLES.map((r) => (
            <option key={r} value={r}>
              {ROLE_LABELS[r]}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        {filteredUsers.map((user) => {
          const isExpanded = expandedUserId === user.id;
          return (
            <div
              key={user.id}
              className="rounded-lg border bg-card overflow-hidden"
            >
              <button
                onClick={() =>
                  setExpandedUserId(isExpanded ? null : user.id)
                }
                className="flex w-full items-center gap-3 p-3 text-left hover:bg-muted/50"
              >
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4 shrink-0" />
                ) : (
                  <ChevronRight className="h-4 w-4 shrink-0" />
                )}
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-medium">
                  {user.email[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{user.email}</p>
                  <p className="text-xs text-muted-foreground truncate">
                    {user.id}
                  </p>
                </div>
                <div className="flex gap-1">
                  {user.roles.map((r) => (
                    <span
                      key={r}
                      className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"
                    >
                      {ROLE_LABELS[r as RoleName] ?? r}
                    </span>
                  ))}
                </div>
                <span
                  className={`h-2 w-2 rounded-full ${
                    user.is_active ? "bg-green-500" : "bg-red-500"
                  }`}
                />
              </button>

              {isExpanded && (
                <div className="border-t p-4 space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">User ID:</span>
                      <span className="ml-2 font-mono text-xs">{user.id}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Email:</span>
                      <span className="ml-2">{user.email}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Status:</span>
                      <span className={`ml-2 ${user.is_active ? "text-green-600" : "text-red-600"}`}>
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                    </div>
                    {user.created_at && (
                      <div>
                        <span className="text-muted-foreground">Created:</span>
                        <span className="ml-2">
                          {new Date(user.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium">Assigned Roles</p>
                    <div className="flex flex-wrap gap-2">
                      {user.roles.map((r) => (
                        <span
                          key={r}
                          className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-1 text-xs"
                        >
                          {ROLE_LABELS[r as RoleName] ?? r}
                          {r !== "admin" && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                revokeRole.mutate({
                                  email: user.email,
                                  role: r,
                                });
                              }}
                              className="ml-1 text-muted-foreground hover:text-destructive"
                              title="Revoke role"
                            >
                              <UserMinus className="h-3 w-3" />
                            </button>
                          )}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium">Add Role</p>
                    <div className="flex flex-wrap gap-2">
                      {ROLES.filter((r) => !user.roles.includes(r)).map((r) => (
                        <button
                          key={r}
                          onClick={() =>
                            assignRole.mutate({ email: user.email, role: r })
                          }
                          className="inline-flex items-center gap-1 rounded-full border px-2 py-1 text-xs hover:bg-muted"
                        >
                          <UserPlus className="h-3 w-3" />
                          {ROLE_LABELS[r]}
                        </button>
                      ))}
                      {ROLES.filter((r) => !user.roles.includes(r)).length ===
                        0 && (
                        <span className="text-xs text-muted-foreground">
                          All roles assigned
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {filteredUsers.length === 0 && (
          <div className="flex h-32 items-center justify-center rounded-lg border border-dashed">
            <p className="text-sm text-muted-foreground">No users found</p>
          </div>
        )}
      </div>
    </div>
  );
}
