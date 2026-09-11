"use client";

import { memo } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  X,
  ExternalLink,
  RefreshCw,
  Ban,
  Clock,
  Activity,
  CheckCircle2,
  XCircle,
  Server,
  FileText,
  AlertTriangle,
} from "lucide-react";
import { useProcessingStore } from "../store/processingStore";
import { useCancelTask, useRetryTask } from "../hooks/useProcessing";
import { ProcessingPipeline } from "./ProcessingPipeline";
import { toast } from "@/components/ui/toast";
import type { DistributedTask } from "@/types/processing";

const STATUS_CONFIG: Record<string, { color: string; icon: React.ReactNode }> = {
  COMPLETED: { color: "bg-emerald-100 text-emerald-700", icon: <CheckCircle2 className="h-3 w-3" /> },
  RUNNING: { color: "bg-blue-100 text-blue-700", icon: <Activity className="h-3 w-3" /> },
  QUEUED: { color: "bg-amber-100 text-amber-700", icon: <Clock className="h-3 w-3" /> },
  FAILED: { color: "bg-red-100 text-red-700", icon: <XCircle className="h-3 w-3" /> },
  CANCELLED: { color: "bg-orange-100 text-orange-700", icon: <Ban className="h-3 w-3" /> },
  RETRYING: { color: "bg-violet-100 text-violet-700", icon: <RefreshCw className="h-3 w-3" /> },
  DEAD_LETTERED: { color: "bg-gray-100 text-gray-700", icon: <AlertTriangle className="h-3 w-3" /> },
};

export const JobDetailsDrawer = memo(function JobDetailsDrawer() {
  const { selectedTask, drawerOpen, setDrawerOpen } = useProcessingStore();
  const cancelTask = useCancelTask();
  const retryTask = useRetryTask();

  if (!drawerOpen || !selectedTask) return null;

  const config = STATUS_CONFIG[selectedTask.status] || STATUS_CONFIG.QUEUED;

  const handleCancel = async () => {
    try {
      await cancelTask.mutateAsync(selectedTask.id);
      toast.add({ title: "Task Cancelled", description: `Task ${selectedTask.id.slice(0, 8)} cancelled.`, type: "success" });
      setDrawerOpen(false);
    } catch {
      toast.add({ title: "Cancel Failed", description: "Could not cancel the task.", type: "error" });
    }
  };

  const handleRetry = async () => {
    try {
      await retryTask.mutateAsync(selectedTask.id);
      toast.add({ title: "Task Re-enqueued", description: `Task ${selectedTask.id.slice(0, 8)} has been re-enqueued.`, type: "success" });
    } catch {
      toast.add({ title: "Retry Failed", description: "Could not retry the task.", type: "error" });
    }
  };

  return (
    <div className="w-[400px] border-l flex flex-col bg-background shrink-0">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          <h3 className="text-sm font-semibold">Task Details</h3>
        </div>
        <div className="flex items-center gap-1">
          {(selectedTask.status === "FAILED" || selectedTask.status === "DEAD_LETTERED") && (
            <Button variant="outline" size="sm" className="h-7 text-xs gap-1" onClick={handleRetry}>
              <RefreshCw className="h-3 w-3" />
              Retry
            </Button>
          )}
          {(selectedTask.status === "QUEUED" || selectedTask.status === "RUNNING") && (
            <Button variant="outline" size="sm" className="h-7 text-xs gap-1 text-destructive" onClick={handleCancel}>
              <Ban className="h-3 w-3" />
              Cancel
            </Button>
          )}
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => setDrawerOpen(false)}>
            <X className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge className={`text-[9px] ${config.color}`}>
                {config.icon}
                {selectedTask.status}
              </Badge>
            </div>
            <h4 className="text-sm font-semibold">{selectedTask.processor_type}</h4>
            <div className="grid grid-cols-2 gap-2 text-[10px] text-muted-foreground">
              <div>
                <span className="font-medium">Task ID:</span>
                <p className="font-mono break-all">{selectedTask.id}</p>
              </div>
              {selectedTask.job_id && (
                <div>
                  <span className="font-medium">Job ID:</span>
                  <p className="font-mono break-all">{selectedTask.job_id}</p>
                </div>
              )}
              <div>
                <span className="font-medium">Priority:</span>
                <p>{selectedTask.priority}</p>
              </div>
              {selectedTask.worker_id && (
                <div>
                  <span className="font-medium">Worker:</span>
                  <p className="font-mono">{selectedTask.worker_id.slice(0, 8)}</p>
                </div>
              )}
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <h5 className="text-xs font-medium">Timestamps</h5>
            <div className="grid grid-cols-2 gap-2 text-[10px] text-muted-foreground">
              {selectedTask.created_at && (
                <div>
                  <span className="font-medium">Created:</span>
                  <p>{new Date(selectedTask.created_at).toLocaleString()}</p>
                </div>
              )}
              {selectedTask.started_at && (
                <div>
                  <span className="font-medium">Started:</span>
                  <p>{new Date(selectedTask.started_at).toLocaleString()}</p>
                </div>
              )}
              {selectedTask.completed_at && (
                <div>
                  <span className="font-medium">Completed:</span>
                  <p>{new Date(selectedTask.completed_at).toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <h5 className="text-xs font-medium">Progress</h5>
            <div className="flex items-center gap-2 text-xs">
              <span>Retries:</span>
              <Badge variant="outline" className="text-[10px]">
                {selectedTask.retry_count ?? 0}/{selectedTask.max_retries ?? 3}
              </Badge>
            </div>
            {selectedTask.progress !== undefined && (
              <div className="flex items-center gap-2">
                <div className="h-2 flex-1 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${selectedTask.progress}%` }}
                  />
                </div>
                <span className="text-[10px] text-muted-foreground">{selectedTask.progress}%</span>
              </div>
            )}
          </div>

          {selectedTask.error && (
            <>
              <Separator />
              <div className="space-y-2">
                <h5 className="text-xs font-medium text-destructive flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  Error
                </h5>
                <div className="p-2 rounded bg-red-50 border border-red-200">
                  <p className="text-xs text-destructive font-mono break-all">
                    {selectedTask.error}
                  </p>
                </div>
              </div>
            </>
          )}

          {selectedTask.payload && Object.keys(selectedTask.payload).length > 0 && (
            <>
              <Separator />
              <div className="space-y-2">
                <h5 className="text-xs font-medium">Payload</h5>
                <pre className="p-2 rounded bg-muted text-[10px] font-mono break-all overflow-x-auto">
                  {JSON.stringify(selectedTask.payload, null, 2)}
                </pre>
              </div>
            </>
          )}

          {selectedTask.dependencies && selectedTask.dependencies.length > 0 && (
            <>
              <Separator />
              <div className="space-y-2">
                <h5 className="text-xs font-medium">Dependencies</h5>
                <div className="flex flex-wrap gap-1">
                  {selectedTask.dependencies.map((dep) => (
                    <Badge key={dep} variant="outline" className="text-[9px] font-mono">
                      {dep.slice(0, 8)}
                    </Badge>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
});
