"use client";

import { useSystemHealth } from "../hooks/useSettings";
import {
  Database,
  HardDrive,
  Circle,
  Server,
  RefreshCw,
} from "lucide-react";

const SERVICE_META: Record<string, { label: string; icon: React.ReactNode }> = {
  database: { label: "Database", icon: <Database className="h-4 w-4" /> },
  redis: { label: "Redis Cache", icon: <HardDrive className="h-4 w-4" /> },
  neo4j: { label: "Neo4j Graph", icon: <Circle className="h-4 w-4" /> },
  minio: { label: "MinIO Storage", icon: <Server className="h-4 w-4" /> },
};

function statusColor(status: string | undefined) {
  if (!status) return "text-muted-foreground";
  const s = status.toLowerCase();
  if (s === "ok" || s === "healthy" || s === "connected" || s === "up")
    return "text-green-600";
  if (s === "degraded" || s === "slow") return "text-amber-600";
  return "text-destructive";
}

function statusDot(status: string | undefined) {
  if (!status) return "bg-muted-foreground";
  const s = status.toLowerCase();
  if (s === "ok" || s === "healthy" || s === "connected" || s === "up")
    return "bg-green-500";
  if (s === "degraded" || s === "slow") return "bg-amber-500";
  return "bg-destructive";
}

export function IntegrationsPanel() {
  const { data: health, isLoading, refetch } = useSystemHealth();

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-16 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    );
  }

  const services = health
    ? Object.entries(health).filter(([key]) => key !== "status" && key !== "uptime")
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Integrations & Health</h2>
          <p className="text-sm text-muted-foreground">
            Backend service connection status.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="inline-flex items-center gap-1 rounded border px-2 py-1 text-xs hover:bg-muted"
        >
          <RefreshCw className="h-3 w-3" />
          Refresh
        </button>
      </div>

      {health?.status && (
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center gap-2">
            <span
              className={`h-2.5 w-2.5 rounded-full ${statusDot(health.status)}`}
            />
            <span className="text-sm font-medium">
              Overall: {health.status}
            </span>
            {health.uptime && (
              <span className="text-xs text-muted-foreground ml-auto">
                Uptime: {health.uptime}
              </span>
            )}
          </div>
        </div>
      )}

      <div className="space-y-2">
        {services.map(([key, value]) => {
          const meta = SERVICE_META[key] ?? {
            label: key,
            icon: <Server className="h-4 w-4" />,
          };
          const statusStr =
            typeof value === "string"
              ? value
              : typeof value === "object"
              ? JSON.stringify(value)
              : String(value);
          return (
            <div
              key={key}
              className="flex items-center gap-3 rounded-lg border bg-card p-3"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded bg-muted">
                {meta.icon}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">{meta.label}</p>
              </div>
              <span
                className={`text-sm font-medium ${statusColor(statusStr)}`}
              >
                {statusStr}
              </span>
              <span
                className={`h-2 w-2 rounded-full ${statusDot(statusStr)}`}
              />
            </div>
          );
        })}

        {services.length === 0 && (
          <div className="flex h-24 items-center justify-center rounded-lg border border-dashed">
            <p className="text-sm text-muted-foreground">
              No service health data available
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
