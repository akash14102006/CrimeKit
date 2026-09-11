"use client";

import { Activity, AlertTriangle, RefreshCw, CheckCircle2, XCircle, Clock } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { useQueueStats } from "@/hooks/queries/useStats";
import { getErrorMessage } from "@/lib/api-client";

function QueueSkeleton() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="p-3 border rounded-lg space-y-2">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-6 w-10" />
          </div>
        ))}
      </div>
      <Skeleton className="h-4 w-full" />
    </div>
  );
}

export function ProcessingQueue() {
  const { data: stats, isLoading, isError, error, refetch } = useQueueStats();

  const total = stats ? stats.queued + stats.running + stats.completed + stats.failed + stats.cancelled : 0;
  const throughput = total > 0 ? Math.round((stats!.completed / total) * 100) : 0;
  const workerUtilization = stats && stats.max_workers > 0
    ? Math.round((stats.active_workers / stats.max_workers) * 100)
    : 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base">Processing Queue</CardTitle>
          <CardDescription>
            {isLoading ? "Loading..." : "Real-time forensic pipeline status"}
          </CardDescription>
        </div>
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => refetch()}
          aria-label="Refresh queue stats"
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
      </CardHeader>
      <CardContent>
        {isError ? (
          <div className="flex flex-col items-center justify-center py-6">
            <AlertTriangle className="h-6 w-6 text-destructive mb-2" />
            <p className="text-sm text-muted-foreground mb-2">
              {error ? getErrorMessage(error) : "Failed to load queue stats"}
            </p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </div>
        ) : isLoading || !stats ? (
          <QueueSkeleton />
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 border rounded-lg">
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Queued
                </p>
                <p className="text-xl font-bold">{stats.queued}</p>
              </div>
              <div className="p-3 border rounded-lg">
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <Activity className="h-3 w-3 text-primary" />
                  Running
                </p>
                <p className="text-xl font-bold">{stats.running}</p>
              </div>
              <div className="p-3 border rounded-lg">
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                  Completed
                </p>
                <p className="text-xl font-bold text-emerald-600">{stats.completed}</p>
              </div>
              <div className="p-3 border rounded-lg">
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <XCircle className="h-3 w-3 text-destructive" />
                  Failed
                </p>
                <p className="text-xl font-bold text-destructive">{stats.failed}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Throughput</span>
                  <span className="text-sm text-muted-foreground">{throughput}%</span>
                </div>
                <Progress value={throughput} />
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Worker Utilization</span>
                  <span className="text-sm text-muted-foreground">
                    {stats.active_workers}/{stats.max_workers}
                  </span>
                </div>
                <Progress value={workerUtilization} />
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
