"use client";

import { useUserProfile } from "../hooks/useSettings";
import { ROLES, ROLE_LABELS } from "@/constants/roles";
import type { RoleName } from "@/types/auth";
import { User, Mail, Shield, Building2, Clock, RotateCcw, AlertCircle } from "lucide-react";
import { getUserInitials, getSafeDisplayName } from "@/lib/userDisplay";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { getErrorMessage } from "@/lib/api-client";

export function ProfilePanel() {
  const { data: profileData, isLoading, error, refetch } = useUserProfile();
  const { user: authUser } = useAuthStore();

  const profile = profileData || authUser;

  if (isLoading && !profile) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
        <div className="h-64 animate-pulse rounded-lg bg-muted" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-8 text-center space-y-4">
        <AlertCircle className="h-8 w-8 text-destructive mx-auto" />
        <div>
          <h3 className="text-sm font-semibold text-destructive">Unable to Load Profile</h3>
          <p className="text-xs text-muted-foreground mt-1">
            {error ? getErrorMessage(error, "Failed to connect to profile service.") : "Profile data is currently unavailable."}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          className="inline-flex items-center gap-2"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>Retry</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Profile</h2>
        <p className="text-sm text-muted-foreground">
          Your account information as synced from the identity provider.
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6 space-y-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-xl font-bold text-primary">
            {getUserInitials(profile.name || profile.email)}
          </div>
          <div>
            <p className="text-lg font-medium">{getSafeDisplayName(profile, profile.email || "Investigator")}</p>
            <p className="text-sm text-muted-foreground">{profile.email}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <Mail className="h-3 w-3" /> Email
            </label>
            <p className="text-sm">{profile.email}</p>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <User className="h-3 w-3" /> User ID
            </label>
            <p className="text-sm font-mono text-xs">{profile.id}</p>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <Shield className="h-3 w-3" /> Roles
            </label>
            <div className="flex flex-wrap gap-1">
              {(profile.roles ?? []).map((r) => (
                <span
                  key={r}
                  className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"
                >
                  {ROLE_LABELS[r as RoleName] ?? r}
                </span>
              ))}
              {(!profile.roles || profile.roles.length === 0) && profile.role && (
                <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                  {ROLE_LABELS[profile.role as RoleName] ?? profile.role}
                </span>
              )}
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <Building2 className="h-3 w-3" /> Organization
            </label>
            <p className="text-sm">{profile.organization || "—"}</p>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <Clock className="h-3 w-3" /> Status
            </label>
            <span
              className={`inline-flex items-center gap-1 text-sm ${
                profile.is_active !== false ? "text-green-600" : "text-red-600"
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  profile.is_active !== false ? "bg-green-500" : "bg-red-500"
                }`}
              />
              {profile.is_active !== false ? "Active" : "Inactive"}
            </span>
          </div>
        </div>

        {profile.permissions && profile.permissions.length > 0 && (
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">
              Permissions
            </label>
            <div className="flex flex-wrap gap-1">
              {profile.permissions.map((p) => (
                <span
                  key={p}
                  className="inline-flex items-center rounded bg-muted px-2 py-0.5 text-xs font-mono"
                >
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
