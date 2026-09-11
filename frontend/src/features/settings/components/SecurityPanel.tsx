"use client";

import { useUserProfile, useAuditVerify } from "../hooks/useSettings";
import { Shield, Key, AlertTriangle, CheckCircle } from "lucide-react";

export function SecurityPanel() {
  const { data: profile } = useUserProfile();
  const { data: auditVerify } = useAuditVerify();

  const roles = profile?.roles ?? [];
  const hasMFA = roles.includes("admin") || roles.includes("compliance_officer");

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Security</h2>
        <p className="text-sm text-muted-foreground">
          View your security status and manage authentication.
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Shield className="h-5 w-5 text-primary" />
          <h3 className="font-medium">Authentication</h3>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="rounded-lg border p-4 space-y-2">
            <div className="flex items-center gap-2">
              <Key className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Identity Provider</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Descope manages authentication, MFA, and session tokens.
            </p>
            <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700">
              <CheckCircle className="h-3 w-3" />
              Connected
            </span>
          </div>

          <div className="rounded-lg border p-4 space-y-2">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">MFA Status</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Multi-factor authentication is managed through Descope flows.
            </p>
            <span
              className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs ${
                hasMFA
                  ? "bg-green-100 text-green-700"
                  : "bg-amber-100 text-amber-700"
              }`}
            >
              {hasMFA ? (
                <>
                  <CheckCircle className="h-3 w-3" />
                  Enforced
                </>
              ) : (
                <>
                  <AlertTriangle className="h-3 w-3" />
                  Available via Descope
                </>
              )}
            </span>
          </div>
        </div>
      </div>

      <div className="rounded-lg border bg-card p-6 space-y-4">
        <h3 className="font-medium">Audit Chain Integrity</h3>
        {auditVerify ? (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Status:</span>
              <span
                className={`ml-2 font-medium ${
                  auditVerify.is_valid ? "text-green-600" : "text-destructive"
                }`}
              >
                {auditVerify.is_valid ? "Valid" : "Broken"}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Chain Length:</span>
              <span className="ml-2 font-medium">
                {auditVerify.chain_length}
              </span>
            </div>
            <div className="col-span-2">
              <span className="text-muted-foreground">Verified At:</span>
              <span className="ml-2">
                {new Date(auditVerify.verified_at).toLocaleString()}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Audit chain data unavailable
          </p>
        )}
      </div>
    </div>
  );
}
