"use client";

import { memo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  BarChart3,
  TrendingUp,
  Clock,
  Users,
  Zap,
} from "lucide-react";
import { useMetrics, useQueueDepth } from "../hooks/useProcessing";
import { useProcessingStore } from "../store/processingStore";

export const QueueAnalytics = memo(function QueueAnalytics() {
  const { data: metrics, isLoading: metricsLoading } = useMetrics();
  const { data: queueDepth, isLoading: depthLoading } = useQueueDepth();

  const isLoading = metricsLoading || depthLoading;

  const successRate = metrics
    ? (metrics.tasks_completed ?? 0) + (metrics.tasks_failed ?? 0) > 0
      ? Math.round(
          ((metrics.tasks_completed ?? 0) /
            ((metrics.tasks_completed ?? 0) + (metrics.tasks_failed ?? 0))) *
            100,
        )
      : 100
    : 0;

  const failureRate = 100 - successRate;

  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          Queue Analytics
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="grid grid-cols-2 gap-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="p-3 border rounded-lg space-y-2">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-6 w-10" />
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 border rounded-lg">
                <div className="flex items-center gap-1.5 mb-1">
                  <TrendingUp className="h-3 w-3 text-emerald-500" />
                  <span className="text-[10px] text-muted-foreground">Success Rate</span>
                </div>
                <p className="text-lg font-bold text-emerald-600">{successRate}%</p>
                <div className="h-1.5 bg-muted rounded-full mt-1 overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${successRate}%` }} />
                </div>
              </div>
              <div className="p-3 border rounded-lg">
                <div className="flex items-center gap-1.5 mb-1">
                  <Zap className="h-3 w-3 text-destructive" />
                  <span className="text-[10px] text-muted-foreground">Failure Rate</span>
                </div>
                <p className="text-lg font-bold text-destructive">{failureRate}%</p>
                <div className="h-1.5 bg-muted rounded-full mt-1 overflow-hidden">
                  <div className="h-full bg-red-500 rounded-full" style={{ width: `${failureRate}%` }} />
                </div>
              </div>
            </div>

            {queueDepth && (
              <div className="space-y-2">
                <h4 className="text-xs font-medium">Queue Depth by Priority</h4>
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { label: "Critical", value: queueDepth.critical ?? 0, color: "bg-red-500" },
                    { label: "High", value: queueDepth.high ?? 0, color: "bg-orange-500" },
                    { label: "Normal", value: queueDepth.normal ?? 0, color: "bg-blue-500" },
                    { label: "Low", value: queueDepth.low ?? 0, color: "bg-gray-400" },
                  ].map((p) => (
                    <div key={p.label} className="p-2 rounded border text-center">
                      <div className="text-[10px] text-muted-foreground mb-1">{p.label}</div>
                      <div className="text-sm font-bold">{p.value}</div>
                      {queueDepth.total && queueDepth.total > 0 && (
                        <div className="h-1 bg-muted rounded-full mt-1 overflow-hidden">
                          <div
                            className={`h-full ${p.color} rounded-full`}
                            style={{ width: `${(p.value / queueDepth.total) * 100}%` }}
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {metrics && (
              <div className="space-y-2">
                <h4 className="text-xs font-medium">System Metrics</h4>
                <div className="grid grid-cols-2 gap-2 text-[10px]">
                  <div className="flex items-center justify-between p-2 rounded border">
                    <span className="text-muted-foreground">Active Workers</span>
                    <Badge variant="secondary">{metrics.active_workers ?? 0}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded border">
                    <span className="text-muted-foreground">Total Workers</span>
                    <Badge variant="secondary">{metrics.total_workers ?? 0}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded border">
                    <span className="text-muted-foreground">Queue Depth</span>
                    <Badge variant="secondary">{metrics.queue_depth ?? 0}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded border">
                    <span className="text-muted-foreground">Uptime</span>
                    <Badge variant="secondary">
                      {metrics.uptime_seconds
                        ? `${Math.round(metrics.uptime_seconds / 3600)}h`
                        : "N/A"}
                    </Badge>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
});
