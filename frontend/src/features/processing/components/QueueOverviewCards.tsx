"use client";

import { memo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Clock,
  Activity,
  CheckCircle2,
  XCircle,
  Ban,
  Cpu,
  Timer,
  Users,
  Server,
  TrendingUp,
} from "lucide-react";
import { useProcessingStore } from "../store/processingStore";
import { useQueueStats, useQueueDepth, useMetrics } from "../hooks/useProcessing";

interface KPICardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color?: string;
  subtitle?: string;
}

function KPICard({ label, value, icon, color = "text-muted-foreground", subtitle }: KPICardProps) {
  return (
    <div className="p-3 border rounded-lg space-y-1">
      <div className="flex items-center gap-1.5">
        <span className={color}>{icon}</span>
        <span className="text-[10px] text-muted-foreground">{label}</span>
      </div>
      <div className="text-xl font-bold">{value}</div>
      {subtitle && (
        <span className="text-[10px] text-muted-foreground">{subtitle}</span>
      )}
    </div>
  );
}

function OverviewSkeleton() {
  return (
    <div className="grid grid-cols-4 lg:grid-cols-6 gap-3">
      {Array.from({ length: 12 }).map((_, i) => (
        <div key={i} className="p-3 border rounded-lg space-y-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-6 w-10" />
        </div>
      ))}
    </div>
  );
}

export const QueueOverviewCards = memo(function QueueOverviewCards() {
  const { queueStats, queueDepth, metrics } = useProcessingStore();
  const { isLoading: statsLoading } = useQueueStats();
  const { isLoading: depthLoading } = useQueueDepth();
  const { isLoading: metricsLoading } = useMetrics();

  if (statsLoading && depthLoading && metricsLoading) {
    return <OverviewSkeleton />;
  }

  const totalJobs = queueStats
    ? queueStats.queued + queueStats.running + queueStats.completed + queueStats.failed + queueStats.cancelled
    : 0;
  const throughput = totalJobs > 0 ? Math.round((queueStats!.completed / totalJobs) * 100) : 0;
  const workerUtil = queueStats && queueStats.max_workers > 0
    ? Math.round((queueStats.active_workers / queueStats.max_workers) * 100)
    : 0;

  return (
    <div className="grid grid-cols-3 lg:grid-cols-6 gap-3">
      <KPICard
        label="Queued"
        value={queueStats?.queued ?? 0}
        icon={<Clock className="h-3.5 w-3.5" />}
        color="text-amber-500"
        subtitle={queueDepth ? `${queueDepth.total ?? 0} in queue` : undefined}
      />
      <KPICard
        label="Running"
        value={queueStats?.running ?? 0}
        icon={<Activity className="h-3.5 w-3.5" />}
        color="text-blue-500"
      />
      <KPICard
        label="Completed"
        value={queueStats?.completed ?? 0}
        icon={<CheckCircle2 className="h-3.5 w-3.5" />}
        color="text-emerald-500"
        subtitle={`${throughput}% throughput`}
      />
      <KPICard
        label="Failed"
        value={queueStats?.failed ?? 0}
        icon={<XCircle className="h-3.5 w-3.5" />}
        color="text-destructive"
      />
      <KPICard
        label="Cancelled"
        value={queueStats?.cancelled ?? 0}
        icon={<Ban className="h-3.5 w-3.5" />}
        color="text-orange-500"
      />
      <KPICard
        label="Workers"
        value={`${queueStats?.active_workers ?? 0}/${queueStats?.max_workers ?? 0}`}
        icon={<Users className="h-3.5 w-3.5" />}
        color="text-violet-500"
        subtitle={`${workerUtil}% utilized`}
      />
    </div>
  );
});
