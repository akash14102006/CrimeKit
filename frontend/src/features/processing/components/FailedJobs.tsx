"use client";

import { memo, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  XCircle,
  RefreshCw,
  AlertTriangle,
  Clock,
  CheckCircle2,
} from "lucide-react";
import { useFailedTasks, useRetryTask, useReplayDLQ } from "../hooks/useProcessing";
import { useProcessingStore } from "../store/processingStore";
import { toast } from "@/components/ui/toast";
import type { DistributedTask } from "@/types/processing";

export const FailedJobs = memo(function FailedJobs() {
  const { data: dlqData, isLoading, refetch } = useFailedTasks();
  const retryTask = useRetryTask();
  const replayDLQ = useReplayDLQ();
  const { selectTask } = useProcessingStore();

  const handleRetry = useCallback(
    async (task: DistributedTask) => {
      try {
        if (task.status === "DEAD_LETTERED") {
          await replayDLQ.mutateAsync(task.id);
        } else {
          await retryTask.mutateAsync(task.id);
        }
        toast.add({
          title: "Task Re-enqueued",
          description: `Task ${task.id.slice(0, 8)} has been re-enqueued.`,
          type: "success",
        });
      } catch {
        toast.add({
          title: "Retry Failed",
          description: "Could not retry the task.",
          type: "error",
        });
      }
    },
    [retryTask, replayDLQ],
  );

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <XCircle className="h-4 w-4 text-destructive" />
          Failed Jobs
          {dlqData && dlqData.total > 0 && (
            <Badge variant="destructive" className="text-[10px]">
              {dlqData.total}
            </Badge>
          )}
        </CardTitle>
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => refetch()}>
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="p-3 border rounded-lg space-y-2">
                <div className="flex items-center gap-2">
                  <Skeleton className="h-4 w-4" />
                  <Skeleton className="h-3 w-20" />
                </div>
                <Skeleton className="h-2 w-full" />
              </div>
            ))}
          </div>
        ) : !dlqData || dlqData.items.length === 0 ? (
          <div className="text-center py-6">
            <CheckCircle2 className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-sm font-medium">No Failed Jobs</p>
            <p className="text-xs text-muted-foreground">All jobs are running successfully.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {dlqData.items.map((item) => {
              const task: DistributedTask = {
                id: item.task_id,
                processor_type: item.processor_type || "unknown",
                status: "FAILED",
                error: item.error,
                retry_count: item.retry_count,
                created_at: item.created_at,
              };
              return (
                <div
                  key={item.task_id}
                  className="p-3 rounded-lg border border-red-200 bg-red-50/50 hover:bg-red-50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <XCircle className="h-3.5 w-3.5 text-destructive" />
                      <span className="text-xs font-mono">{item.task_id.slice(0, 8)}</span>
                      <Badge variant="destructive" className="text-[9px]">FAILED</Badge>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 text-[10px] gap-1"
                        onClick={() => handleRetry(task)}
                      >
                        <RefreshCw className="h-2.5 w-2.5" />
                        Retry
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={() => selectTask(task)}
                      >
                        <AlertTriangle className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>

                  {item.processor_type && (
                    <p className="text-[10px] text-muted-foreground mb-1">
                      Processor: {item.processor_type}
                    </p>
                  )}

                  {item.error && (
                    <p className="text-[10px] text-destructive line-clamp-2 font-mono">
                      {item.error}
                    </p>
                  )}

                  <div className="flex items-center gap-3 mt-1.5 text-[10px] text-muted-foreground">
                    {item.created_at && (
                      <span className="flex items-center gap-0.5">
                        <Clock className="h-2.5 w-2.5" />
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                    )}
                    {item.retry_count !== undefined && (
                      <span>Retries: {item.retry_count}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
});


