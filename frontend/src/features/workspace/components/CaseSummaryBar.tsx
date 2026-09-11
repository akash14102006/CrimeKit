"use client";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Briefcase,
  Users,
  FileText,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Upload,
} from "lucide-react";
import { useWorkspace, useWorkspaceProgress, useWorkspaceRisks } from "@/hooks/queries/useWorkspace";
import { useCaseEvidence } from "@/hooks/queries/useEvidence";
import { formatBytes } from "@/lib/utils";

interface Props {
  caseId: string;
}

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, string> = {
    open: "bg-blue-100 text-blue-800 border-blue-200",
    "in_review": "bg-amber-100 text-amber-800 border-amber-200",
    closed: "bg-emerald-100 text-emerald-800 border-emerald-200",
  };
  return (
    <Badge variant="outline" className={variants[status] ?? "bg-gray-100 text-gray-800"}>
      {status?.replace("_", " ")}
    </Badge>
  );
}

function PriorityBadge({ priority }: { priority: string }) {
  const variants: Record<string, string> = {
    critical: "bg-red-100 text-red-800 border-red-200",
    high: "bg-orange-100 text-orange-800 border-orange-200",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
    low: "bg-gray-100 text-gray-800 border-gray-200",
  };
  return (
    <Badge variant="outline" className={variants[priority] ?? "bg-gray-100 text-gray-800"}>
      {priority}
    </Badge>
  );
}

export function CaseSummaryBar({ caseId }: Props) {
  const { data: workspace, isLoading } = useWorkspace(caseId);
  const { data: evidence } = useCaseEvidence(caseId);
  const { data: progress } = useWorkspaceProgress(caseId);
  const { data: risks } = useWorkspaceRisks(caseId);

  if (isLoading) {
    return (
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <Skeleton className="h-6 w-[200px]" />
          <Skeleton className="h-6 w-[80px]" />
          <Skeleton className="h-6 w-[80px]" />
          <div className="flex-1" />
          <Skeleton className="h-4 w-[100px]" />
        </div>
      </Card>
    );
  }

  const caseData = workspace?.case;
  const totalEvidence = evidence?.length ?? 0;
  const totalSize = evidence?.reduce((sum, ev) => sum + (ev.size || 0), 0) ?? 0;
  const riskCount = risks?.length ?? 0;
  const highRiskCount = (risks?.filter((r) => r.severity === "high") ?? []).length;

  return (
    <Card className="p-4">
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <Briefcase className="h-4 w-4 text-muted-foreground" />
          <span className="font-semibold text-sm">
            {caseData?.title ?? "Investigation"}
          </span>
        </div>

        {caseData?.status && <StatusBadge status={caseData.status} />}
        {caseData?.priority && <PriorityBadge priority={caseData.priority} />}

        <div className="h-4 w-px bg-border" />

        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <FileText className="h-3.5 w-3.5" />
          <span>{totalEvidence} evidence</span>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Upload className="h-3.5 w-3.5" />
          <span>{formatBytes(totalSize)}</span>
        </div>

        {progress && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>{progress.completion_percent}% processed</span>
          </div>
        )}

        <div className="flex-1" />

        {riskCount > 0 && (
          <div className="flex items-center gap-1.5 text-xs">
            <AlertTriangle className={`h-3.5 w-3.5 ${highRiskCount > 0 ? "text-red-500" : "text-amber-500"}`} />
            <span className={highRiskCount > 0 ? "text-red-600" : "text-amber-600"}>
              {riskCount} risk{riskCount !== 1 ? "s" : ""}
            </span>
          </div>
        )}

        {caseData?.assigned_to && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Users className="h-3.5 w-3.5" />
            <span>{caseData.assigned_to}</span>
          </div>
        )}

        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Clock className="h-3.5 w-3.5" />
          <span>{new Date().toLocaleDateString()}</span>
        </div>
      </div>
    </Card>
  );
}
