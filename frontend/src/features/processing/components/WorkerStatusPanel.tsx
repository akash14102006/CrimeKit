"use client";

import { memo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Server,
  Cpu,
  MemoryStick,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
  Wifi,
  WifiOff,
} from "lucide-react";
import { useWorkers } from "../hooks/useProcessing";
import { useProcessingStore } from "../store/processingStore";
import type { WorkerInfo } from "@/types/processing";

const STATUS_CONFIG: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  idle: {
    color: "bg-emerald-100 text-emerald-700",
    icon: <CheckCircle2 className="h-3 w-3" />,
    label: "Idle",
  },
  busy: {
    color: "bg-blue-100 text-blue-700",
    icon: <Cpu className="h-3 w-3" />,
    label: "Busy",
  },
  offline: {
    color: "bg-red-100 text-red-700",
    icon: <WifiOff className="h-3 w-3" />,
    label: "Offline",
  },
  restarting: {
    color: "bg-amber-100 text-amber-700",
    icon: <RefreshCw className="h-3 w-3 animate-spin" />,
    label: "Restarting",
  },
};

function WorkerCard({ worker }: { worker: WorkerInfo }) {
  const { selectWorker } = useProcessingStore();
  const config = STATUS_CONFIG[worker.status] || STATUS_CONFIG.idle;
  const [isStale] = useState(() =>
    worker.last_heartbeat ? Date.now() - new Date(worker.last_heartbeat).getTime() > 60000 : false,
  );

  return (
    <div
      className={`p-3 rounded-lg border cursor-pointer transition-colors hover:bg-muted/30 ${
        isStale ? "border-amber-300 bg-amber-50/50" : ""
      }`}
      onClick={() => selectWorker(worker)}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Server className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-xs font-medium">{worker.worker_id.slice(0, 8)}</span>
        </div>
        <Badge className={`text-[9px] ${config.color}`}>
          {config.icon}
          {config.label}
        </Badge>
      </div>

      {worker.name && (
        <p className="text-[10px] text-muted-foreground mb-2">{worker.name}</p>
      )}

      <div className="grid grid-cols-2 gap-2 mb-2">
        <div>
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground mb-0.5">
            <Cpu className="h-2.5 w-2.5" />
            CPU
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-1.5 flex-1 bg-muted rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  (worker.cpu_usage ?? 0) > 80 ? "bg-red-500" : "bg-primary"
                }`}
                style={{ width: `${worker.cpu_usage ?? 0}%` }}
              />
            </div>
            <span className="text-[10px] text-muted-foreground w-8 text-right">
              {worker.cpu_usage ?? 0}%
            </span>
          </div>
        </div>
        <div>
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground mb-0.5">
            <MemoryStick className="h-2.5 w-2.5" />
            Memory
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-1.5 flex-1 bg-muted rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  (worker.memory_usage ?? 0) > 80 ? "bg-red-500" : "bg-primary"
                }`}
                style={{ width: `${worker.memory_usage ?? 0}%` }}
              />
            </div>
            <span className="text-[10px] text-muted-foreground w-8 text-right">
              {worker.memory_usage ?? 0}%
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between text-[10px] text-muted-foreground">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-0.5">
            <CheckCircle2 className="h-2.5 w-2.5 text-emerald-500" />
            {worker.tasks_completed ?? 0}
          </span>
          <span className="flex items-center gap-0.5">
            <XCircle className="h-2.5 w-2.5 text-red-500" />
            {worker.tasks_failed ?? 0}
          </span>
        </div>
        {worker.current_task_id && (
          <Badge variant="outline" className="text-[8px]">
            Running task
          </Badge>
        )}
      </div>

      {worker.last_heartbeat && (
        <div className="flex items-center gap-1 mt-1.5 text-[9px] text-muted-foreground">
          <Wifi className="h-2 w-2" />
          {isStale ? (
            <span className="text-amber-600">Stale heartbeat</span>
          ) : (
            <span>Last seen {new Date(worker.last_heartbeat).toLocaleTimeString()}</span>
          )}
        </div>
      )}

      {worker.capabilities && worker.capabilities.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {worker.capabilities.slice(0, 3).map((cap) => (
            <Badge key={cap} variant="outline" className="text-[8px]">
              {cap}
            </Badge>
          ))}
          {worker.capabilities.length > 3 && (
            <Badge variant="outline" className="text-[8px]">
              +{worker.capabilities.length - 3}
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}

function WorkerSkeleton() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="p-3 border rounded-lg space-y-2">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-2 w-full" />
          <Skeleton className="h-2 w-3/4" />
        </div>
      ))}
    </div>
  );
}

export const WorkerStatusPanel = memo(function WorkerStatusPanel() {
  const { data, isLoading, isError, refetch } = useWorkers();
  const workers = data?.workers ?? [];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Server className="h-4 w-4" />
          Worker Status
          {workers.length > 0 && (
            <Badge variant="secondary" className="text-[10px]">
              {workers.length}
            </Badge>
          )}
        </CardTitle>
        <Button
          variant="ghost"
          size="sm"
          className="h-7 w-7 p-0"
          onClick={() => refetch()}
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <WorkerSkeleton />
        ) : isError ? (
          <div className="text-center py-4">
            <WifiOff className="h-6 w-6 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-xs text-muted-foreground">Failed to load workers</p>
            <Button variant="outline" size="sm" className="mt-2" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        ) : workers.length === 0 ? (
          <div className="text-center py-4">
            <Server className="h-6 w-6 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-xs text-muted-foreground">No workers registered</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {workers.map((worker) => (
              <WorkerCard key={worker.worker_id} worker={worker} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
});
