"use client";

import { useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Lightbulb,
  Upload,
  FileSearch,
  CalendarClock,
  Shield,
  FileText,
  Play,
  ExternalLink,
} from "lucide-react";
import { useWorkspace, useWorkspaceProgress, useWorkspaceRisks } from "@/hooks/queries/useWorkspace";
import { useRouter } from "next/navigation";

interface SuggestedAction {
  id: string;
  label: string;
  reason: string;
  priority: "high" | "medium" | "low";
  icon: React.ReactNode;
  href?: string;
  onClick?: () => void;
}

export function SuggestedActionsPanel({ caseId }: { caseId: string }) {
  const router = useRouter();
  const { data: workspace } = useWorkspace(caseId);
  const { data: progress } = useWorkspaceProgress(caseId);
  const { data: risks } = useWorkspaceRisks(caseId);

  const actions: SuggestedAction[] = useMemo(() => {
    const result: SuggestedAction[] = [];

    if (progress) {
      if (progress.completion_percent < 50) {
        result.push({
          id: "upload-more",
          label: "Upload More Evidence",
          reason: `Only ${progress.completion_percent}% of evidence processed. More data strengthens the investigation.`,
          priority: "high",
          icon: <Upload className="h-4 w-4" />,
          href: "/evidence",
        });
      }

      if (
        progress.forensic_jobs_failed > 0 &&
        progress.forensic_jobs_total > 0
      ) {
        result.push({
          id: "reprocess",
          label: "Reprocess Failed Evidence",
          reason: `${progress.forensic_jobs_failed} forensic jobs failed. Retry processing to extract more data.`,
          priority: "high",
          icon: <Play className="h-4 w-4" />,
        });
      }

      if (
        progress.evidence_with_documents === 0 &&
        progress.evidence_total > 0
      ) {
        result.push({
          id: "run-ocr",
          label: "Run OCR Processing",
          reason: "No text extracted yet. Run OCR to enable entity extraction and search.",
          priority: "high",
          icon: <FileSearch className="h-4 w-4" />,
        });
      }

      if (
        progress.completion_percent >= 50 &&
        progress.forensic_jobs_completed > 0
      ) {
        result.push({
          id: "review-timeline",
          label: "Review Timeline",
          reason: "Processing complete. Review chronological events to identify patterns.",
          priority: "medium",
          icon: <CalendarClock className="h-4 w-4" />,
          href: "/timeline",
        });
      }
    }

    if (risks && risks.length > 0) {
      const highRisks = risks.filter((r) => r.severity === "high");
      if (highRisks.length > 0) {
        result.push({
          id: "review-risks",
          label: "Review Risk Indicators",
          reason: `${highRisks.length} high-severity risks detected. Immediate attention recommended.`,
          priority: "high",
          icon: <Shield className="h-4 w-4" />,
        });
      }
    }

    if (workspace) {
      if (workspace.ai_findings && workspace.ai_findings.length > 0) {
        result.push({
          id: "generate-report",
          label: "Generate Court Report",
          reason: `${workspace.ai_findings.length} AI findings available. Generate a court-ready report.`,
          priority: "medium",
          icon: <FileText className="h-4 w-4" />,
        });
      }

      if (
        workspace.timeline &&
        workspace.timeline.length > 0 &&
        (!workspace.ai_findings || workspace.ai_findings.length === 0)
      ) {
        result.push({
          id: "ai-analyze",
          label: "Run AI Analysis",
          reason: "Timeline data available. Run AI analysis to generate findings and correlations.",
          priority: "medium",
          icon: <FileSearch className="h-4 w-4" />,
        });
      }
    }

    if (result.length === 0) {
      result.push({
        id: "upload-evidence",
        label: "Upload Evidence",
        reason: "Start by uploading evidence files to begin the investigation.",
        priority: "medium",
        icon: <Upload className="h-4 w-4" />,
        href: "/evidence",
      });
    }

    return result;
  }, [progress, risks, workspace]);

  const priorityColors: Record<string, string> = {
    high: "border-red-200 bg-red-50/50",
    medium: "border-amber-200 bg-amber-50/50",
    low: "border-blue-200 bg-blue-50/50",
  };

  const priorityBadge: Record<string, string> = {
    high: "bg-red-100 text-red-700",
    medium: "bg-amber-100 text-amber-700",
    low: "bg-blue-100 text-blue-700",
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b">
        <Lightbulb className="h-4 w-4 text-amber-500" />
        <h3 className="text-sm font-semibold">Suggested Actions</h3>
        <Badge variant="secondary" className="text-[10px]">
          {actions.length}
        </Badge>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {actions.map((action) => (
            <div
              key={action.id}
              className={`rounded-lg border p-3 space-y-2 ${priorityColors[action.priority]}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <div className="text-primary">{action.icon}</div>
                  <span className="text-sm font-medium">{action.label}</span>
                </div>
                <Badge
                  variant="outline"
                  className={`text-[10px] ${priorityBadge[action.priority]}`}
                >
                  {action.priority}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">{action.reason}</p>
              <div className="flex gap-2">
                {action.href ? (
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs gap-1"
                    onClick={() => router.push(action.href!)}
                  >
                    <ExternalLink className="h-3 w-3" />
                    Go
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs"
                    onClick={action.onClick}
                  >
                    Take Action
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
