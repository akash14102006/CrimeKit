/** Dashboard-specific types aligned to verified backend contracts. */

export interface MetricsResponse {
  request_count: Record<string, number>;
  error_count: Record<string, number>;
  forensic_jobs: Record<string, number>;
  uptime_seconds: number;
}

export interface ActivityEvent {
  id: string;
  action: string;
  target_type: string;
  target_id: string;
  actor_id: string;
  detail: Record<string, unknown>;
  timestamp: string;
}

export interface ActivityFeedResponse {
  events: ActivityEvent[];
  total: number;
}

/** Derived KPI computed from /cases, /evidence, /processing/queue/stats, /health/detailed */
export interface DashboardKPI {
  totalCases: number;
  activeCases: number;
  totalEvidence: number;
  queuedJobs: number;
  runningJobs: number;
  completedJobs: number;
  failedJobs: number;
  activeWorkers: number;
  maxWorkers: number;
  systemHealth: "healthy" | "degraded" | "unknown";
  healthChecks: Array<{
    service: string;
    status: string;
    latency_ms: number;
  }>;
}
