"use client";

import { ShieldCheck, ShieldOff, AlertTriangle } from "lucide-react";
import { useAdminUsers } from "../hooks/useAdmin";

export function MFAPanel() {
  const { data: users, isLoading } = useAdminUsers();

  const mfaStats = {
    total: users?.length ?? 0,
    note: "MFA status is managed via Descope. The backend MFAConfig model tracks TOTP enrollment. Full MFA admin requires Descope Management API integration.",
  };

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-20 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <ShieldCheck className="h-5 w-5" />
        <h2 className="text-lg font-semibold">MFA Management</h2>
      </div>

      <div className="rounded-lg border bg-card p-4 space-y-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-amber-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Descope-Managed MFA</p>
            <p className="text-sm text-muted-foreground">
              Multi-factor authentication is managed through Descope&apos;s identity
              platform. MFA enrollment, verification, and recovery codes are
              handled by Descope&apos;s SDK and flows.
            </p>
          </div>
        </div>

        <div className="rounded-lg bg-muted/50 p-3 text-sm">
          <p className="font-medium mb-1">Backend MFA Model Status</p>
          <p className="text-muted-foreground">
            The <code className="font-mono text-xs">mfa_configs</code> table
            stores TOTP secrets and enrollment status per user. The{" "}
            <code className="font-mono text-xs">POST /auth/mfa/verify</code>{" "}
            endpoint validates TOTP codes. Full admin management requires
            Descope Management API integration for user-level MFA controls.
          </p>
        </div>

        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="rounded-lg border p-3">
            <p className="text-2xl font-bold">{mfaStats.total}</p>
            <p className="text-xs text-muted-foreground">Total Users</p>
          </div>
          <div className="rounded-lg border p-3">
            <div className="flex justify-center">
              <ShieldCheck className="h-6 w-6 text-green-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-1">Enforced via Descope</p>
          </div>
          <div className="rounded-lg border p-3">
            <div className="flex justify-center">
              <ShieldOff className="h-6 w-4 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground mt-1">Admin controls pending</p>
          </div>
        </div>
      </div>
    </div>
  );
}
