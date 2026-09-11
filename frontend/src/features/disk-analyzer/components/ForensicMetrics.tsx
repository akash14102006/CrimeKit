"use client";

import { HardDrive, FolderTree, File, Trash2, AlertTriangle, Clock, Activity, Database, Layers } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";
import { formatBytes } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: typeof HardDrive;
  description?: string;
  variant?: "default" | "success" | "warning" | "destructive";
}

function MetricCard({ title, value, icon: Icon, description, variant = "default" }: MetricCardProps) {
  const colorMap = {
    default: "text-primary",
    success: "text-success",
    warning: "text-warning",
    destructive: "text-destructive",
  };

  return (
    <Card className="py-3">
      <CardContent className="flex items-center gap-3 px-4">
        <div className={`rounded-md bg-muted p-2 ${colorMap[variant]}`}>
          <Icon className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[10px] uppercase text-muted-foreground">{title}</p>
          <p className="text-lg font-bold leading-tight">{value}</p>
          {description && (
            <p className="text-[10px] text-muted-foreground">{description}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function ForensicMetrics() {
  const { metrics, artifacts, timeline, partitions, filesystems, processing } = useDiskAnalyzerStore();

  if (!metrics && !processing) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-6 text-center">
        <Activity className="mb-2 h-8 w-8 text-muted-foreground/30" />
        <p className="text-xs text-muted-foreground">
          Run TSK analysis to view forensic metrics
        </p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <div className="text-center">
          <Activity className="mx-auto mb-2 h-6 w-6 animate-pulse text-primary" />
          <p className="text-xs text-muted-foreground">Processing...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Forensic Metrics
      </h3>
      <div className="grid grid-cols-4 gap-2">
        <MetricCard
          title="Partitions"
          value={partitions.length}
          icon={Layers}
          description={`${filesystems.length} filesystem(s)`}
        />
        <MetricCard
          title="Files"
          value={metrics.total_files.toLocaleString()}
          icon={File}
          description={`${metrics.total_directories.toLocaleString()} dirs`}
        />
        <MetricCard
          title="Artifacts"
          value={artifacts.length.toLocaleString()}
          icon={Database}
          variant="success"
        />
        <MetricCard
          title="Timeline Events"
          value={timeline.length.toLocaleString()}
          icon={Clock}
          variant="success"
        />
      </div>
      <div className="mt-2 grid grid-cols-4 gap-2">
        <MetricCard
          title="Deleted"
          value={metrics.total_deleted.toLocaleString()}
          icon={Trash2}
          variant="warning"
          description="Deleted files found"
        />
        <MetricCard
          title="Unallocated"
          value={metrics.total_unallocated.toLocaleString()}
          icon={AlertTriangle}
          variant="warning"
          description="Unallocated space"
        />
        <MetricCard
          title="Orphan"
          value={metrics.total_orphan.toLocaleString()}
          icon={FolderTree}
          variant="warning"
          description="Orphan inodes"
        />
        <MetricCard
          title="Total Size"
          value={formatBytes(metrics.total_size_bytes)}
          icon={HardDrive}
          description="Disk content size"
        />
      </div>
      <div className="mt-2 grid grid-cols-4 gap-2">
        <MetricCard
          title="Processing Time"
          value={`${(metrics.processing_time_ms / 1000).toFixed(1)}s`}
          icon={Clock}
        />
        <MetricCard
          title="Image Size"
          value={formatBytes(metrics.total_size_bytes)}
          icon={HardDrive}
        />
        <MetricCard
          title="Orphan Inodes"
          value={metrics.total_orphan.toLocaleString()}
          icon={FolderTree}
        />
        <MetricCard
          title="Events"
          value={timeline.length.toLocaleString()}
          icon={Activity}
          variant={timeline.length > 0 ? "success" : "default"}
        />
      </div>
    </div>
  );
}
