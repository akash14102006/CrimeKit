"use client";

import { memo, useCallback, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Activity,
  Clock,
  Play,
  Pause,
  CheckCircle2,
  XCircle,
  Ban,
  RefreshCw,
  Eye,
} from "lucide-react";
import { useQueueStats, useCancelTask } from "../hooks/useProcessing";
import { useProcessingStore } from "../store/processingStore";
import { toast } from "@/components/ui/toast";
import type { QueueStats } from "@/types/processing";

const STATUS_ICONS: Record<string, React.ReactNode> = {
  queued: <Clock className="h-3.5 w-3.5 text-amber-500" />,
  running: <Activity className="h-3.5 w-3.5 text-blue-500 animate-pulse" />,
  completed: <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />,
  failed: <XCircle className="h-3.5 w-3.5 text-destructive" />,
  cancelled: <Ban className="h-3.5 w-3.5 text-orange-500" />,
};

const STATUS_BADGE: Record<string, string> = {
  queued: "bg-amber-100 text-amber-700",
  running: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
  cancelled: "bg-orange-100 text-orange-700",
};

interface JobCardProps {
  jobId: string;
  status: string;
  evidenceId?: string;
  processors?: string[];
  queuedAt?: string;
  startedAt?: string;
  onCancel?: (jobId: string) => void;
  onView?: (jobId: string) => void;
}

function JobCard({ jobId, status, evidenceId, processors, queuedAt, startedAt, onCancel, onView }: JobCardProps) {
  const [elapsed] = useState(() =>
    startedAt ? Math.max(0, Math.floor((Date.now() - new Date(startedAt).getTime()) / 1000)) : null,
  );

  return (
    <div className="p-3 rounded-lg border hover:bg-muted/30 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {STATUS_ICONS[status] || STATUS_ICONS.queued}
          <span className="text-xs font-mono">{jobId.slice(0, 8)}</span>
          <Badge className={`text-[9px] ${STATUS_BADGE[status] || ""}`}>
            {status}
          </Badge>
        </div>
        <div className="flex items-center gap-1">
          {onView && (
            <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={() => onView(jobId)}>
              <Eye className="h-3 w-3" />
            </Button>
          )}
          {(status === "queued" || status === "running") && onCancel && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 text-destructive"
              onClick={() => onCancel(jobId)}
            >
              <Ban className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>

      {evidenceId && (
        <p className="text-[10px] text-muted-foreground mb-1">
          Evidence: {evidenceId.slice(0, 12)}
        </p>
      )}

      {processors && processors.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {processors.slice(0, 3).map((p) => (
            <Badge key={p} variant="outline" className="text-[8px]">
              {p}
            </Badge>
          ))}
          {processors.length > 3 && (
            <Badge variant="outline" className="text-[8px]">
              +{processors.length - 3}
            </Badge>
          )}
        </div>
      )}

      <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
        {queuedAt && (
          <span className="flex items-center gap-0.5">
            <Clock className="h-2.5 w-2.5" />
            Queued {new Date(queuedAt).toLocaleTimeString()}
          </span>
        )}
        {elapsed !== null && (
          <span className="flex items-center gap-0.5">
            <Activity className="h-2.5 w-2.5" />
            {elapsed}s elapsed
          </span>
        )}
      </div>
    </div>
  );
}

function JobListSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="p-3 border rounded-lg space-y-2">
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-4" />
            <Skeleton className="h-3 w-20" />
            <Skeleton className="h-4 w-12" />
          </div>
          <Skeleton className="h-2 w-full" />
        </div>
      ))}
    </div>
  );
}

export const LiveJobs = memo(function LiveJobs() {
  const { data: stats, isLoading, refetch } = useQueueStats();
  const cancelTask = useCancelTask();
  const { selectTask } = useProcessingStore();

  const handleCancel = useCallback(
    async (jobId: string) => {
      try {
        await cancelTask.mutateAsync(jobId);
        toast.add({ title: "Job Cancelled", description: `Job ${jobId.slice(0, 8)} has been cancelled.`, type: "success" });
      } catch {
        toast.add({ title: "Cancel Failed", description: "Could not cancel the job.", type: "error" });
      }
    },
    [cancelTask],
  );

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Activity className="h-4 w-4" />
          Processing Queue
          {stats && stats.queued + stats.running > 0 && (
            <Badge variant="secondary" className="text-[10px]">
              {stats.queued + stats.running} active
            </Badge>
          )}
        </CardTitle>
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => refetch()}>
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <JobListSkeleton />
        ) : !stats || (stats.queued === 0 && stats.running === 0) ? (
          <div className="text-center py-6">
            <CheckCircle2 className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-sm font-medium">Queue Empty</p>
            <p className="text-xs text-muted-foreground">
              All jobs have been processed. Upload evidence to start processing.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {stats.running > 0 && (
              <div>
                <h4 className="text-xs font-medium mb-2 flex items-center gap-1">
                  <Activity className="h-3 w-3 text-blue-500" />
                  Running ({stats.running})
                </h4>
                <div className="space-y-2">
                  <JobCard
                    jobId={`running-${stats.running}`}
                    status="running"
                    onCancel={handleCancel}
                    onView={(id) => selectTask({ id, processor_type: "processing", status: "RUNNING" })}
                  />
                </div>
              </div>
            )}

            {stats.queued > 0 && (
              <div>
                <h4 className="text-xs font-medium mb-2 flex items-center gap-1">
                  <Clock className="h-3 w-3 text-amber-500" />
                  Queued ({stats.queued})
                </h4>
                <div className="space-y-2">
                  {Array.from({ length: Math.min(stats.queued, 5) }).map((_, i) => (
                    <JobCard
                      key={`queued-${i}`}
                      jobId={`queued-${i}`}
                      status="queued"
                      onCancel={handleCancel}
                      onView={(id) => selectTask({ id, processor_type: "processing", status: "QUEUED" })}
                    />
                  ))}
                  {stats.queued > 5 && (
                    <p className="text-[10px] text-muted-foreground text-center">
                      +{stats.queued - 5} more jobs in queue
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
});
