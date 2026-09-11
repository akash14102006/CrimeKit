"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  Brain,
  Cpu,
  AlertTriangle,
  RefreshCw,
  Shield,
} from "lucide-react";
import {
  useWorkspaceAIFindings,
  useWorkspaceProgress,
  useWorkspaceRisks,
} from "@/hooks/queries/useWorkspace";
import { useQueueStats } from "@/hooks/queries/useStats";
import { useWorkspaceStore } from "@/store/workspaceStore";

interface Props {
  caseId: string;
}

function SeverityBadge({ severity }: { severity: string }) {
  const variants: Record<string, string> = {
    high: "bg-red-100 text-red-800 border-red-200",
    medium: "bg-amber-100 text-amber-800 border-amber-200",
    low: "bg-blue-100 text-blue-800 border-blue-200",
  };
  return (
    <Badge variant="outline" className={variants[severity] ?? "bg-gray-100 text-gray-800"}>
      {severity}
    </Badge>
  );
}

function AIInsights({ caseId }: { caseId: string }) {
  const { data: findings, isLoading, refetch } = useWorkspaceAIFindings(caseId);

  if (isLoading) {
    return (
      <div className="space-y-3 p-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3 p-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold flex items-center gap-1.5">
          <Brain className="h-3.5 w-3.5" />
          AI Findings
        </h4>
        <Button variant="ghost" size="sm" className="h-6 px-2" onClick={() => refetch()}>
          <RefreshCw className="h-3 w-3" />
        </Button>
      </div>

      {!findings || findings.length === 0 ? (
        <div className="text-center py-4">
          <Brain className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
          <p className="text-xs text-muted-foreground">No AI findings yet</p>
          <p className="text-[10px] text-muted-foreground mt-1">Upload evidence and run processing to generate insights</p>
        </div>
      ) : (
        <div className="space-y-2">
          {findings.slice(0, 10).map((finding, i) => (
            <div key={i} className="p-2 rounded-md border bg-muted/30 text-xs space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-medium truncate flex-1">
                  {finding.snippet?.slice(0, 60) ?? `Finding #${i + 1}`}
                </span>
                <Badge variant="outline" className="text-[10px] ml-2">
                  {(finding.score * 100).toFixed(0)}%
                </Badge>
              </div>
              {finding.evidence_id && (
                <p className="text-[10px] text-muted-foreground">
                  Evidence: {finding.evidence_id.slice(0, 8)}...
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ProcessingStatus({ caseId }: { caseId: string }) {
  const { data: progress, isLoading } = useWorkspaceProgress(caseId);
  const { data: queueStats } = useQueueStats();

  if (isLoading) {
    return (
      <div className="space-y-3 p-3">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    );
  }

  return (
    <div className="space-y-3 p-3">
      <h4 className="text-xs font-semibold flex items-center gap-1.5">
        <Cpu className="h-3.5 w-3.5" />
        Processing Status
      </h4>

      {progress && (
        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Completion</span>
            <span className="font-medium">{progress.completion_percent}%</span>
          </div>
          <div className="h-1.5 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all"
              style={{ width: `${progress.completion_percent}%` }}
            />
          </div>
          <div className="grid grid-cols-3 gap-2 text-center text-[10px]">
            <div className="p-1.5 rounded bg-muted/50">
              <p className="font-medium text-foreground">{progress.forensic_jobs_completed}</p>
              <p className="text-muted-foreground">Done</p>
            </div>
            <div className="p-1.5 rounded bg-muted/50">
              <p className="font-medium text-foreground">{progress.forensic_jobs_total - progress.forensic_jobs_completed - progress.forensic_jobs_failed}</p>
              <p className="text-muted-foreground">Running</p>
            </div>
            <div className="p-1.5 rounded bg-muted/50">
              <p className="font-medium text-foreground">{progress.forensic_jobs_failed}</p>
              <p className="text-muted-foreground">Failed</p>
            </div>
          </div>
        </div>
      )}

      {queueStats && (
        <div className="space-y-1 text-[10px]">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Queue depth</span>
            <span>{queueStats.queued + queueStats.running}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Completed</span>
            <span>{queueStats.completed}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Failed</span>
            <span className={queueStats.failed > 0 ? "text-red-500" : ""}>{queueStats.failed}</span>
          </div>
        </div>
      )}
    </div>
  );
}

function RiskPanel({ caseId }: { caseId: string }) {
  const { data: risks, isLoading } = useWorkspaceRisks(caseId);

  if (isLoading) {
    return (
      <div className="space-y-3 p-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3 p-3">
      <h4 className="text-xs font-semibold flex items-center gap-1.5">
        <AlertTriangle className="h-3.5 w-3.5" />
        Risk Indicators
      </h4>

      {!risks || risks.length === 0 ? (
        <div className="text-center py-4">
          <Shield className="h-8 w-8 mx-auto text-green-500 mb-2" />
          <p className="text-xs text-green-600 font-medium">No risks detected</p>
          <p className="text-[10px] text-muted-foreground mt-1">All checks passed for this investigation</p>
        </div>
      ) : (
        <div className="space-y-2">
          {risks.map((risk, i) => (
            <div key={i} className="p-2 rounded-md border text-xs space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-medium">{risk.code}</span>
                <SeverityBadge severity={risk.severity} />
              </div>
              <p className="text-muted-foreground text-[10px]">{risk.message}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function RightPanel({ caseId }: Props) {
  const { rightPanelTab, setRightPanelTab } = useWorkspaceStore();

  return (
    <div className="flex h-full flex-col">
      <Tabs
        value={rightPanelTab}
        onValueChange={(v) => setRightPanelTab(v as "ai" | "processing" | "risks")}
        className="flex h-full flex-col"
      >
        <TabsList className="grid w-full grid-cols-3 h-9 mx-2 mt-2 w-[calc(100%-16px)]">
          <TabsTrigger value="ai" className="text-[10px] gap-1">
            <Brain className="h-3 w-3" />
            AI
          </TabsTrigger>
          <TabsTrigger value="processing" className="text-[10px] gap-1">
            <Cpu className="h-3 w-3" />
            Processing
          </TabsTrigger>
          <TabsTrigger value="risks" className="text-[10px] gap-1">
            <AlertTriangle className="h-3 w-3" />
            Risks
          </TabsTrigger>
        </TabsList>

        <TabsContent value="ai" className="flex-1 overflow-hidden mt-0">
          <ScrollArea className="h-full">
            <AIInsights caseId={caseId} />
          </ScrollArea>
        </TabsContent>

        <TabsContent value="processing" className="flex-1 overflow-hidden mt-0">
          <ScrollArea className="h-full">
            <ProcessingStatus caseId={caseId} />
          </ScrollArea>
        </TabsContent>

        <TabsContent value="risks" className="flex-1 overflow-hidden mt-0">
          <ScrollArea className="h-full">
            <RiskPanel caseId={caseId} />
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}
