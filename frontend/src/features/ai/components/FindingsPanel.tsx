"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Brain,
  FileText,
  RefreshCw,
  ExternalLink,
} from "lucide-react";
import { useWorkspaceAIFindings } from "@/hooks/queries/useWorkspace";

export function FindingsPanel({ caseId }: { caseId: string }) {
  const { data: findings, isLoading, refetch } = useWorkspaceAIFindings(caseId);

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <Brain className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-semibold">AI Findings</h3>
          {findings && findings.length > 0 && (
            <Badge variant="secondary" className="text-[10px]">
              {findings.length}
            </Badge>
          )}
        </div>
        <Button variant="ghost" size="sm" onClick={() => refetch()}>
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {!findings || findings.length === 0 ? (
            <div className="text-center py-12">
              <Brain className="h-12 w-12 mx-auto text-muted-foreground/20 mb-3" />
              <h4 className="text-sm font-medium mb-1">No Findings Yet</h4>
              <p className="text-xs text-muted-foreground max-w-xs mx-auto">
                Upload evidence and run processing to generate AI-powered
                findings and insights.
              </p>
            </div>
          ) : (
            findings.map((finding, i) => (
              <div
                key={i}
                className="rounded-lg border p-3 space-y-2 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm leading-relaxed flex-1">
                    {finding.snippet || `Finding #${i + 1}`}
                  </p>
                  <Badge variant="outline" className="text-[10px] shrink-0">
                    {(finding.score * 100).toFixed(0)}%
                  </Badge>
                </div>
                {finding.evidence_id && (
                  <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                    <FileText className="h-3 w-3" />
                    <span>Evidence: {finding.evidence_id.slice(0, 12)}...</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-4 w-4 p-0 ml-auto"
                      onClick={() =>
                        window.open(
                          `/evidence/${finding.evidence_id}`,
                          "_blank",
                        )
                      }
                    >
                      <ExternalLink className="h-2.5 w-2.5" />
                    </Button>
                  </div>
                )}
                <div className="h-1 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary/60 rounded-full"
                    style={{ width: `${finding.score * 100}%` }}
                  />
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
