"use client";

import {
  Briefcase,
  FileText,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Users,
  Server,
  Clock,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useDashboardKPI } from "@/hooks/queries/useDashboard";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

interface KPIItemProps {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  tone?: "default" | "success" | "warning" | "destructive";
}

function KPIItem({ title, value, description, icon, tone = "default" }: KPIItemProps) {
  const toneColors = {
    default: "text-muted-foreground",
    success: "text-emerald-500",
    warning: "text-amber-500",
    destructive: "text-destructive",
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <span className={toneColors[tone]}>{icon}</span>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

function KPISkeleton() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-4 rounded" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-16 mb-1" />
        <Skeleton className="h-3 w-32" />
      </CardContent>
    </Card>
  );
}

function KPIError({ onRetry }: { onRetry: () => void }) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-8">
        <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
        <p className="text-sm text-muted-foreground mb-2">Failed to load KPIs</p>
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RefreshCw className="h-3 w-3 mr-1" />
          Retry
        </Button>
      </CardContent>
    </Card>
  );
}

export function KPIRow() {
  const { data, isLoading, isError, refetch } = useDashboardKPI();

  if (isError) {
    return (
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <KPIError key={i} onRetry={() => refetch()} />
        ))}
      </div>
    );
  }

  if (isLoading || !data) {
    return (
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <KPISkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
      <KPIItem
        title="Total Cases"
        value={data.totalCases}
        description={`${data.activeCases} active`}
        icon={<Briefcase className="h-4 w-4" />}
      />
      <KPIItem
        title="Active Cases"
        value={data.activeCases}
        description="Currently open"
        icon={<Clock className="h-4 w-4" />}
        tone={data.activeCases > 0 ? "warning" : "default"}
      />
      <KPIItem
        title="Evidence Items"
        value={data.totalEvidence}
        description="Uploaded evidence"
        icon={<FileText className="h-4 w-4" />}
      />
      <KPIItem
        title="Processing Queue"
        value={data.queuedJobs + data.runningJobs}
        description={`${data.runningJobs} running, ${data.queuedJobs} queued`}
        icon={<Activity className="h-4 w-4" />}
        tone={data.queuedJobs > 5 ? "warning" : "default"}
      />
      <KPIItem
        title="Completed Jobs"
        value={data.completedJobs}
        description="Successfully processed"
        icon={<CheckCircle2 className="h-4 w-4" />}
        tone="success"
      />
      <KPIItem
        title="Failed Jobs"
        value={data.failedJobs}
        description="Requires attention"
        icon={<AlertTriangle className="h-4 w-4" />}
        tone={data.failedJobs > 0 ? "destructive" : "success"}
      />
      <KPIItem
        title="System Health"
        value={data.systemHealth === "healthy" ? "Healthy" : "Degraded"}
        description={`${data.healthChecks.length} services monitored`}
        icon={<Server className="h-4 w-4" />}
        tone={data.systemHealth === "healthy" ? "success" : "destructive"}
      />
      <KPIItem
        title="Workers"
        value={`${data.activeWorkers}/${data.maxWorkers}`}
        description="Active / Max"
        icon={<Users className="h-4 w-4" />}
        tone={data.activeWorkers >= data.maxWorkers ? "warning" : "default"}
      />
    </div>
  );
}
