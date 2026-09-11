"use client";

import { useQuery } from "@tanstack/react-query";
import { useCases } from "./useCases";
import { useQueueStats, useSystemHealth } from "./useStats";
import { useAllEvidence } from "./useEvidence";
import { observabilityService } from "@/services/observabilityService";

/** Dashboard KPI: combines cases, evidence, queue stats, and health into a single derived object. */
export function useDashboardKPI() {
  const cases = useCases({ page: 1, limit: 100 });
  const evidenceResponse = useAllEvidence({ page: 1, limit: 100 });
  const queueStats = useQueueStats();
  const health = useSystemHealth();

  const isLoading =
    cases.isLoading || evidenceResponse.isLoading || queueStats.isLoading || health.isLoading;
  const isError = cases.isError || evidenceResponse.isError || queueStats.isError || health.isError;
  const error = cases.error || evidenceResponse.error || queueStats.error || health.error;

  const caseItems = cases.data?.items ?? [];
  const data =
    cases.data && evidenceResponse.data && queueStats.data && health.data
      ? {
          totalCases: cases.data.total,
          activeCases: caseItems.filter(
            (c) => c.status !== "closed",
          ).length,
          totalEvidence: evidenceResponse.data.total,
          queuedJobs: queueStats.data.queued,
          runningJobs: queueStats.data.running,
          completedJobs: queueStats.data.completed,
          failedJobs: queueStats.data.failed,
          activeWorkers: queueStats.data.active_workers,
          maxWorkers: queueStats.data.max_workers,
          systemHealth: health.data.status,
          healthChecks: (health.data.checks ?? []).map((c) => ({
            service: c.service,
            status: c.status,
            latency_ms: c.latency_ms,
          })),
        }
      : undefined;

  const refetch = () => {
    cases.refetch();
    evidenceResponse.refetch();
    queueStats.refetch();
    health.refetch();
  };

  return { data, isLoading, isError, error, refetch };
}

/** Observability metrics for charts. */
export function useMetrics() {
  return useQuery({
    queryKey: ["dashboard", "metrics"],
    queryFn: () => observabilityService.metricsJson(),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

/** Cases summary for charts (status breakdown, created dates). */
export function useCasesSummary() {
  const { data: response, isLoading, isError, error, refetch } = useCases({ page: 1, limit: 100 });
  const cases = response?.items;

  const summary = cases
    ? {
        total: response?.total ?? cases.length,
        open: cases.filter((c) => c.status === "open").length,
        closed: cases.filter((c) => c.status === "closed").length,
        review: cases.filter((c) => c.status === "review").length,
        byStatus: [
          { name: "Open", value: cases.filter((c) => c.status === "open").length },
          { name: "Closed", value: cases.filter((c) => c.status === "closed").length },
          { name: "Review", value: cases.filter((c) => c.status === "review").length },
        ],
      }
    : undefined;

  return { data: summary, isLoading, isError, error, refetch };
}

/** Evidence summary for charts (type breakdown). */
export function useEvidenceSummary() {
  const { data: response, isLoading, isError, error, refetch } = useAllEvidence({ page: 1, limit: 100 });
  const evidence = response?.items;

  const summary = evidence
    ? {
        total: response?.total ?? evidence.length,
        byType: evidence.reduce(
          (acc: Record<string, number>, e) => {
            const type = e.mime_type?.split("/")[0] || "unknown";
            acc[type] = (acc[type] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>,
        ),
      }
    : undefined;

  return { data: summary, isLoading, isError, error, refetch };
}
