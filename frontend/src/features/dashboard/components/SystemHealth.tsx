"use client";

import { AlertTriangle, RefreshCw, CheckCircle2, XCircle, Clock } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useSystemHealth } from "@/hooks/queries/useStats";
import { getErrorMessage } from "@/lib/api-client";

function HealthSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex items-center justify-between p-2 border rounded">
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-4 rounded" />
            <Skeleton className="h-4 w-20" />
          </div>
          <Skeleton className="h-5 w-14 rounded" />
        </div>
      ))}
    </div>
  );
}

function statusColor(status: string): "default" | "secondary" | "destructive" | "outline" {
  if (status === "healthy") return "default";
  if (status === "unhealthy" || status === "degraded") return "destructive";
  return "secondary";
}

function statusIcon(status: string) {
  if (status === "healthy") return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
  if (status === "unhealthy") return <XCircle className="h-4 w-4 text-destructive" />;
  return <AlertTriangle className="h-4 w-4 text-amber-500" />;
}

export function SystemHealth() {
  const { data: health, isLoading, isError, error, refetch } = useSystemHealth();

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base">System Health</CardTitle>
          <CardDescription>
            {isLoading
              ? "Loading..."
              : health?.status === "healthy"
                ? "All systems operational"
                : "Degraded performance detected"}
          </CardDescription>
        </div>
        <div className="flex items-center gap-2">
          {health?.version && (
            <Badge variant="outline" className="text-xs">
              v{health.version}
            </Badge>
          )}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => refetch()}
            aria-label="Refresh health"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isError ? (
          <div className="flex flex-col items-center justify-center py-6">
            <AlertTriangle className="h-6 w-6 text-destructive mb-2" />
            <p className="text-sm text-muted-foreground mb-2">
              {error ? getErrorMessage(error) : "Failed to load health"}
            </p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </div>
        ) : isLoading || !health ? (
          <HealthSkeleton />
        ) : (
          <div className="space-y-2">
            <div className="flex items-center justify-between p-2 border rounded-lg">
              <div className="flex items-center gap-2">
                {statusIcon(health.status)}
                <span className="text-sm font-medium">Overall</span>
              </div>
              <Badge variant={statusColor(health.status)}>
                {health.status}
              </Badge>
            </div>
            {health.checks.map((check) => (
              <div
                key={check.service}
                className="flex items-center justify-between p-2 border rounded-lg"
              >
                <div className="flex items-center gap-2">
                  {statusIcon(check.status)}
                  <span className="text-sm">{check.service}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {check.latency_ms.toFixed(1)}ms
                  </span>
                  <Badge variant={statusColor(check.status)} className="text-xs">
                    {check.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
