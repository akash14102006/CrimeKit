"use client";

import { ClipboardList, CheckCircle, AlertCircle, RefreshCw } from "lucide-react";
import { useAuditVerify, useSystemHealth } from "../hooks/useAdmin";

export function AuditPanel() {
  const { data: auditVerify, isLoading: auditLoading, refetch: refetchAudit } = useAuditVerify();
  const { data: health, isLoading: healthLoading } = useSystemHealth();

  if (auditLoading || healthLoading) {
    return (
      <div className="space-y-3">
        <div className="h-20 animate-pulse rounded-lg bg-muted" />
        <div className="h-32 animate-pulse rounded-lg bg-muted" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ClipboardList className="h-5 w-5" />
          <h2 className="text-lg font-semibold">Audit Summary</h2>
        </div>
        <button
          onClick={() => refetchAudit()}
          className="inline-flex items-center gap-1 rounded border px-2 py-1 text-xs hover:bg-muted"
        >
          <RefreshCw className="h-3 w-3" />
          Verify Chain
        </button>
      </div>

      <div className="rounded-lg border bg-card p-4 space-y-3">
        <h3 className="text-sm font-medium">Audit Chain Integrity</h3>
        {auditVerify ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              {auditVerify.is_valid ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-destructive" />
              )}
              <span className="text-sm font-medium">
                {auditVerify.is_valid ? "Chain Valid" : "Chain Broken"}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-muted-foreground">Chain Length:</span>
                <span className="ml-2 font-medium">{auditVerify.chain_length}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Verified At:</span>
                <span className="ml-2">
                  {new Date(auditVerify.verified_at).toLocaleString()}
                </span>
              </div>
              {auditVerify.broken_at && (
                <div className="col-span-2">
                  <span className="text-muted-foreground">Broken At:</span>
                  <span className="ml-2 text-destructive font-mono text-xs">
                    {auditVerify.broken_at}
                  </span>
                </div>
              )}
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            No audit chain data available
          </p>
        )}
      </div>

      {health && (
        <div className="rounded-lg border bg-card p-4 space-y-3">
          <h3 className="text-sm font-medium">System Health</h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(health).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-muted-foreground capitalize">
                  {key.replace(/_/g, " ")}:
                </span>
                <span className="font-mono text-xs">
                  {typeof value === "object" ? JSON.stringify(value) : String(value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
