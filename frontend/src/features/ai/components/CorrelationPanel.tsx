"use client";

import { useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { GitBranch, ExternalLink } from "lucide-react";
import { useWorkspace } from "@/hooks/queries/useWorkspace";

export function CorrelationPanel({ caseId }: { caseId: string }) {
  const { data: workspace, isLoading } = useWorkspace(caseId);

  const correlations = useMemo(() => {
    if (!workspace) return [];
    const results: Array<{
      type: string;
      title: string;
      confidence: number;
      detail: string;
      evidenceIds: string[];
    }> = [];

    if (workspace.related_evidence && workspace.related_evidence.length > 0) {
      for (const rel of workspace.related_evidence) {
        results.push({
          type: "Evidence Correlation",
          title: `Evidence ${rel.evidence_id.slice(0, 8)} ↔ ${rel.related_evidence_id.slice(0, 8)}`,
          confidence: rel.similarity,
          detail: rel.reason,
          evidenceIds: [rel.evidence_id, rel.related_evidence_id],
        });
      }
    }

    if (workspace.similar_cases && workspace.similar_cases.length > 0) {
      for (const sim of workspace.similar_cases) {
        results.push({
          type: "Similar Case",
          title: sim.title,
          confidence: sim.similarity,
          detail: sim.reason,
          evidenceIds: [],
        });
      }
    }

    if (workspace.knowledge_graph) {
      const kg = workspace.knowledge_graph;
      if (kg.entity_count && kg.entity_count > 0) {
        results.push({
          type: "Knowledge Graph",
          title: `${kg.entity_count} entities, ${kg.relationship_count || 0} relationships`,
          confidence: 0.9,
          detail: `Graph source: ${kg.source || "SQLite fallback"}`,
          evidenceIds: [],
        });
      }
    }

    if (workspace.timeline && workspace.timeline.length > 0) {
      const dates = workspace.timeline
        .map((t) => t.date || t.timestamp)
        .filter(Boolean)
        .sort();
      if (dates.length > 1) {
        results.push({
          type: "Timeline Correlation",
          title: `${workspace.timeline.length} events spanning ${dates[0]} to ${dates[dates.length - 1]}`,
          confidence: 0.85,
          detail: "Temporal patterns detected across evidence timeline",
          evidenceIds: workspace.timeline
            .map((t) => t.source_id)
            .filter(Boolean) as string[],
        });
      }
    }

    return results;
  }, [workspace]);

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b">
        <GitBranch className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold">Correlations</h3>
        {correlations.length > 0 && (
          <Badge variant="secondary" className="text-[10px]">
            {correlations.length}
          </Badge>
        )}
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {correlations.length === 0 ? (
            <div className="text-center py-12">
              <GitBranch className="h-12 w-12 mx-auto text-muted-foreground/20 mb-3" />
              <h4 className="text-sm font-medium mb-1">No Correlations Found</h4>
              <p className="text-xs text-muted-foreground max-w-xs mx-auto">
                Process more evidence to enable cross-correlation analysis
                between evidence items, entities, and timeline events.
              </p>
            </div>
          ) : (
            correlations.map((corr, i) => (
              <div
                key={i}
                className="rounded-lg border p-3 space-y-2 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Badge
                      variant="outline"
                      className="text-[10px] mb-1"
                    >
                      {corr.type}
                    </Badge>
                    <p className="text-sm font-medium">{corr.title}</p>
                  </div>
                  <Badge variant="secondary" className="text-[10px] shrink-0">
                    {(corr.confidence * 100).toFixed(0)}%
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{corr.detail}</p>
                {corr.evidenceIds.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {corr.evidenceIds.map((eid) => (
                      <a
                        key={eid}
                        href={`/evidence/${eid}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-[10px] text-primary hover:underline"
                      >
                        {eid.slice(0, 8)}...
                        <ExternalLink className="h-2.5 w-2.5" />
                      </a>
                    ))}
                  </div>
                )}
                <div className="h-1 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary/60 rounded-full"
                    style={{ width: `${corr.confidence * 100}%` }}
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
