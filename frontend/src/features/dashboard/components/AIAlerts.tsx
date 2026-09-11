"use client";

import { Brain, AlertTriangle, RefreshCw, Shield, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useCases } from "@/hooks/queries/useCases";
import { useQuery } from "@tanstack/react-query";
import { workspaceService } from "@/services/workspaceService";
import { useRBAC } from "@/hooks/useRBAC";
import { getErrorMessage } from "@/lib/api-client";

interface Alert {
  id: string;
  severity: "high" | "medium" | "low";
  message: string;
  caseId: string;
  caseTitle: string;
}

function AlertSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="p-3 border rounded-lg space-y-2">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-5 w-14 rounded" />
          </div>
          <Skeleton className="h-3 w-full" />
        </div>
      ))}
    </div>
  );
}

/** Fetch AI findings and risk indicators from first few active cases. */
function useAIAlerts() {
  const { data: casesResponse, isLoading: casesLoading } = useCases({ page: 1, limit: 100 });
  const cases = casesResponse?.items;
  const activeCaseIds = cases?.filter((c) => c.status !== "closed").slice(0, 5).map((c) => c.id) ?? [];

  const findings = useQuery({
    queryKey: ["dashboard", "ai-alerts", activeCaseIds],
    queryFn: async () => {
      const alerts: Alert[] = [];
      for (const caseId of activeCaseIds) {
        try {
          const [risks, findings] = await Promise.all([
            workspaceService.risks(caseId).catch(() => []),
            workspaceService.aiFindings(caseId).catch(() => []),
          ]);

          for (const risk of risks) {
            alerts.push({
              id: `risk-${caseId}-${risk.code}`,
              severity: risk.severity,
              message: risk.message,
              caseId,
              caseTitle: cases?.find((c) => c.id === caseId)?.title ?? caseId.slice(0, 8),
            });
          }

          for (const finding of findings.slice(0, 2)) {
            if (finding.score > 0.7) {
              alerts.push({
                id: `ai-${caseId}-${finding.document_id}`,
                severity: finding.score > 0.9 ? "high" : "medium",
                message: `AI finding: ${(finding.snippet ?? "Suspicious content detected").slice(0, 100)}...`,
                caseId,
                caseTitle: cases?.find((c) => c.id === caseId)?.title ?? caseId.slice(0, 8),
              });
            }
          }
        } catch {
          // Skip failed cases
        }
      }
      return alerts;
    },
    enabled: activeCaseIds.length > 0,
    staleTime: 60_000,
  });

  return {
    data: findings.data ?? [],
    isLoading: casesLoading || findings.isLoading,
    isError: findings.isError,
    error: findings.error,
    refetch: findings.refetch,
  };
}

export function AIAlerts() {
  const { hasPermission } = useRBAC();
  const { data: alerts, isLoading, isError, error, refetch } = useAIAlerts();

  const canView = hasPermission("kg:query") || hasPermission("case:read");
  if (!canView) return null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base">AI Intelligence</CardTitle>
          <CardDescription>
            {isLoading
              ? "Analyzing cases..."
              : `${alerts.length} alert${alerts.length !== 1 ? "s" : ""} from active investigations`}
          </CardDescription>
        </div>
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => refetch()}
          aria-label="Refresh AI alerts"
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
      </CardHeader>
      <CardContent>
        {isError ? (
          <div className="flex flex-col items-center justify-center py-6">
            <AlertTriangle className="h-6 w-6 text-destructive mb-2" />
            <p className="text-sm text-muted-foreground mb-2">
              {error ? getErrorMessage(error) : "Failed to load AI alerts"}
            </p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </div>
        ) : isLoading ? (
          <AlertSkeleton />
        ) : alerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <Brain className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">No AI alerts</p>
            <p className="text-xs text-muted-foreground mt-1">
              All active investigations are within normal parameters
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {alerts.slice(0, 5).map((alert) => (
              <div
                key={alert.id}
                className="p-3 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    {alert.severity === "high" ? (
                      <Shield className="h-4 w-4 text-destructive" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-amber-500" />
                    )}
                    <span className="text-sm font-medium">{alert.caseTitle}</span>
                  </div>
                  <Badge
                    variant={
                      alert.severity === "high"
                        ? "destructive"
                        : alert.severity === "medium"
                          ? "secondary"
                          : "outline"
                    }
                  >
                    {alert.severity}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {alert.message}
                </p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
