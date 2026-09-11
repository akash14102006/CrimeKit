"use client";

import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import {
  FileText,
  AlertTriangle,
  Clock,
  BookOpen,
} from "lucide-react";
import { useWorkspace, useWorkspaceProgress, useWorkspaceCourtReport } from "@/hooks/queries/useWorkspace";

export function InvestigationSummaryPanel({ caseId }: { caseId: string }) {
  const { data: workspace, isLoading: wsLoading } = useWorkspace(caseId);
  const { data: progress, isLoading: progLoading } = useWorkspaceProgress(caseId);
  const { data: courtReport, isLoading: courtLoading } = useWorkspaceCourtReport(caseId);

  const isLoading = wsLoading || progLoading || courtLoading;

  if (isLoading) {
    return (
      <div className="space-y-4 p-4">
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    );
  }

  const evidenceCount = workspace?.evidence?.length ?? 0;
  const timelineCount = workspace?.timeline?.length ?? 0;
  const findingsCount = workspace?.ai_findings?.length ?? 0;
  const risksCount = workspace?.risk_indicators?.length ?? 0;
  const highRisks =
    (workspace?.risk_indicators?.filter((r) => r.severity === "high") ?? []).length;
  const entitiesCount = workspace?.knowledge_graph?.entity_count ?? 0;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b">
        <BookOpen className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold">Investigation Summary</h3>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {workspace?.case && (
            <div className="rounded-lg border p-3 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold">{workspace.case.title}</h4>
                <Badge variant="outline" className="text-[10px]">
                  {workspace.case.status}
                </Badge>
              </div>
              {workspace.case.description && (
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {workspace.case.description}
                </p>
              )}
            </div>
          )}

          <div className="grid grid-cols-3 gap-2">
            <div className="text-center p-2 rounded bg-muted/50">
              <div className="text-lg font-bold">{evidenceCount}</div>
              <div className="text-[10px] text-muted-foreground">Evidence</div>
            </div>
            <div className="text-center p-2 rounded bg-muted/50">
              <div className="text-lg font-bold">{entitiesCount}</div>
              <div className="text-[10px] text-muted-foreground">Entities</div>
            </div>
            <div className="text-center p-2 rounded bg-muted/50">
              <div className="text-lg font-bold">{timelineCount}</div>
              <div className="text-[10px] text-muted-foreground">Events</div>
            </div>
          </div>

          {progress && (
            <div className="rounded-lg border p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium">Processing Progress</span>
                <span className="text-xs text-muted-foreground">
                  {progress.completion_percent}%
                </span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full transition-all"
                  style={{ width: `${progress.completion_percent}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-muted-foreground">
                <span>
                  {progress.forensic_jobs_completed}/{progress.forensic_jobs_total} jobs
                </span>
                <span>{progress.evidence_with_documents} docs extracted</span>
              </div>
            </div>
          )}

          <div className="rounded-lg border p-3 space-y-2">
            <h4 className="text-xs font-medium">Key Metrics</h4>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">AI Findings</span>
                <Badge variant="secondary" className="text-[10px]">
                  {findingsCount}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Risk Indicators</span>
                <Badge
                  variant="secondary"
                  className={`text-[10px] ${highRisks > 0 ? "bg-red-100 text-red-700" : ""}`}
                >
                  {risksCount}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">KG Entities</span>
                <Badge variant="secondary" className="text-[10px]">
                  {entitiesCount}
                </Badge>
              </div>
            </div>
          </div>

          {courtReport && (
            <div className="rounded-lg border p-3 space-y-2">
              <div className="flex items-center gap-2">
                <FileText className="h-3.5 w-3.5" />
                <span className="text-xs font-medium">Court Report</span>
              </div>
              <div className="flex items-center justify-between">
                <Badge
                  variant="outline"
                  className={`text-[10px] ${
                    courtReport.status === "ready"
                      ? "bg-green-100 text-green-700"
                      : courtReport.status === "blocked"
                        ? "bg-red-100 text-red-700"
                        : ""
                  }`}
                >
                  {courtReport.status}
                </Badge>
                <span className="text-[10px] text-muted-foreground">
                  {courtReport.completion_percent}%
                </span>
              </div>
            </div>
          )}

          {workspace?.risk_indicators && workspace.risk_indicators.length > 0 && (
            <div className="rounded-lg border p-3 space-y-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
                <span className="text-xs font-medium">Open Risks</span>
              </div>
              <div className="space-y-1">
                {workspace.risk_indicators.slice(0, 5).map((risk, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 text-xs"
                  >
                    {risk.severity === "high" ? (
                      <AlertTriangle className="h-3 w-3 text-red-500 shrink-0" />
                    ) : (
                      <Clock className="h-3 w-3 text-muted-foreground shrink-0" />
                    )}
                    <span className="truncate">{risk.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
