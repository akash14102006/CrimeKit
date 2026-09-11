"use client";

import { memo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  History,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Ban,
  Clock,
  Download,
} from "lucide-react";
import { useMetrics } from "../hooks/useProcessing";
import { useProcessingStore } from "../store/processingStore";

export const ProcessingHistory = memo(function ProcessingHistory() {
  const { data: metrics, isLoading, refetch } = useMetrics();
  const { selectTask } = useProcessingStore();

  const stats = [
    {
      label: "Tasks Completed",
      value: metrics?.tasks_completed ?? 0,
      icon: <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />,
      color: "text-emerald-600",
    },
    {
      label: "Tasks Failed",
      value: metrics?.tasks_failed ?? 0,
      icon: <XCircle className="h-3.5 w-3.5 text-destructive" />,
      color: "text-destructive",
    },
    {
      label: "Tasks Retried",
      value: metrics?.tasks_retried ?? 0,
      icon: <RefreshCw className="h-3.5 w-3.5 text-violet-500" />,
      color: "text-violet-600",
    },
    {
      label: "Dead-Lettered",
      value: metrics?.tasks_dead_lettered ?? 0,
      icon: <Ban className="h-3.5 w-3.5 text-orange-500" />,
      color: "text-orange-600",
    },
    {
      label: "Tasks Submitted",
      value: metrics?.tasks_submitted ?? 0,
      icon: <Clock className="h-3.5 w-3.5 text-blue-500" />,
      color: "text-blue-600",
    },
    {
      label: "Uptime",
      value: metrics?.uptime_seconds
        ? `${Math.round(metrics.uptime_seconds / 3600)}h`
        : "N/A",
      icon: <Clock className="h-3.5 w-3.5 text-muted-foreground" />,
      color: "text-muted-foreground",
    },
  ];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <History className="h-4 w-4" />
          Processing History
        </CardTitle>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" className="h-7 text-[10px] gap-1">
            <Download className="h-3 w-3" />
            Export
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => refetch()}>
            <RefreshCw className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="grid grid-cols-3 gap-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="p-3 border rounded-lg space-y-2">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-6 w-10" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            {stats.map((stat) => (
              <div key={stat.label} className="p-3 border rounded-lg">
                <div className="flex items-center gap-1.5 mb-1">
                  {stat.icon}
                  <span className="text-[10px] text-muted-foreground">{stat.label}</span>
                </div>
                <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
});
