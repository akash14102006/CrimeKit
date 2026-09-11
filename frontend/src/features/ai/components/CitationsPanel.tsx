"use client";

import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import {
  FileText,
  CalendarClock,
  GitBranch,
  Cpu,
  ExternalLink,
} from "lucide-react";
import { useWorkspaceAIFindings } from "@/hooks/queries/useWorkspace";
import { useCaseTimeline } from "@/hooks/queries/useTimeline";

export function CitationsPanel({ caseId }: { caseId: string }) {
  const { data: findings } = useWorkspaceAIFindings(caseId);
  const { data: timeline } = useCaseTimeline(caseId);

  const citations: Array<{
    id: string;
    type: "evidence" | "timeline" | "kg" | "processing" | "report";
    label: string;
    source_id: string;
    confidence?: number;
  }> = [];

  if (findings) {
    for (const f of findings) {
      if (f.evidence_id) {
        citations.push({
          id: `find-${f.document_id}`,
          type: "evidence",
          label: `Finding: ${f.snippet?.slice(0, 40) || f.document_id.slice(0, 8)}`,
          source_id: f.evidence_id,
          confidence: f.score,
        });
      }
    }
  }

  if (timeline) {
    for (const t of timeline.slice(0, 10)) {
      citations.push({
        id: `tl-${t.id}`,
        type: "timeline",
        label: t.title || `Event ${t.timestamp}`,
        source_id: t.evidence_id || t.id,
      });
    }
  }

  const typeIcons: Record<string, React.ReactNode> = {
    evidence: <FileText className="h-3 w-3" />,
    timeline: <CalendarClock className="h-3 w-3" />,
    kg: <GitBranch className="h-3 w-3" />,
    processing: <Cpu className="h-3 w-3" />,
    report: <FileText className="h-3 w-3" />,
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b">
        <FileText className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold">Source Citations</h3>
        <Badge variant="secondary" className="text-[10px]">
          {citations.length}
        </Badge>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-2">
          {citations.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground/20 mb-3" />
              <h4 className="text-sm font-medium mb-1">No Citations</h4>
              <p className="text-xs text-muted-foreground max-w-xs mx-auto">
                Citations will appear here as AI findings and timeline events
                are generated from processed evidence.
              </p>
            </div>
          ) : (
            citations.map((cite) => (
              <div
                key={cite.id}
                className="flex items-center gap-3 p-2 rounded-md hover:bg-muted/30 transition-colors"
              >
                <div className="text-muted-foreground">{typeIcons[cite.type]}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium truncate">{cite.label}</p>
                  <p className="text-[10px] text-muted-foreground">
                    {cite.type}: {cite.source_id.slice(0, 12)}
                  </p>
                </div>
                {cite.confidence != null && (
                  <Badge variant="outline" className="text-[10px] shrink-0">
                    {(cite.confidence * 100).toFixed(0)}%
                  </Badge>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 shrink-0"
                  onClick={() =>
                    window.open(`/evidence/${cite.source_id}`, "_blank")
                  }
                >
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
