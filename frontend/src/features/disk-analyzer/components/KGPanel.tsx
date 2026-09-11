"use client";

import { useMemo } from "react";
import { Network, Link2, ExternalLink } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";
import type { TSKArtifact } from "@/types/tsk";

interface GraphNode {
  id: string;
  label: string;
  type: "evidence" | "file" | "entity" | "artifact";
  count?: number;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

function buildGraphFromArtifacts(
  evidenceId: string,
  artifacts: TSKArtifact[],
): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const nodes: GraphNode[] = [
    { id: `evidence:${evidenceId}`, label: evidenceId.slice(0, 12), type: "evidence" },
  ];
  const edges: GraphEdge[] = [];
  const seenTypes = new Map<string, number>();

  for (const artifact of artifacts) {
    const fileNode: GraphNode = {
      id: `file:${artifact.file_path}`,
      label: artifact.file_name,
      type: "file",
    };
    nodes.push(fileNode);
    edges.push({
      source: `evidence:${evidenceId}`,
      target: `file:${artifact.file_path}`,
      type: "contains",
    });

    const typeKey = artifact.filesystem_type ?? "unknown";
    const count = seenTypes.get(typeKey) ?? 0;
    seenTypes.set(typeKey, count + 1);

    if (count === 0) {
      nodes.push({
        id: `fs:${typeKey}`,
        label: typeKey.toUpperCase(),
        type: "entity",
      });
    }

    edges.push({
      source: `file:${artifact.file_path}`,
      target: `fs:${typeKey}`,
      type: "filesystem",
    });
  }

  return { nodes, edges };
}

const NODE_COLORS: Record<string, string> = {
  evidence: "bg-primary/10 text-primary border-primary/30",
  file: "bg-info/10 text-info border-info/30",
  entity: "bg-success/10 text-success border-success/30",
  artifact: "bg-warning/10 text-warning border-warning/30",
};

export function KGPanel() {
  const { evidenceId, artifacts, caseId } = useDiskAnalyzerStore();
  const graph = useMemo(
    () => buildGraphFromArtifacts(evidenceId ?? "", artifacts),
    [evidenceId, artifacts],
  );

  if (graph.nodes.length <= 1) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-6 text-center">
        <Network className="mb-2 h-8 w-8 text-muted-foreground/30" />
        <p className="text-xs text-muted-foreground">
          No knowledge graph data. Run TSK analysis to build the graph.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b px-4 py-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Knowledge Graph
        </h3>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-[10px]">
            {graph.nodes.length} nodes
          </Badge>
          <Badge variant="secondary" className="text-[10px]">
            {graph.edges.length} edges
          </Badge>
          {caseId && (
            <a
              href={`/kg/${caseId}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-6 items-center gap-1 rounded-md px-2 text-[10px] text-muted-foreground hover:bg-accent hover:text-foreground"
            >
              <ExternalLink className="h-2.5 w-2.5" />
              Full KG
            </a>
          )}
        </div>
      </div>
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs">Graph Nodes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {graph.nodes.map((node) => (
                <div
                  key={node.id}
                  className="flex items-center gap-2 rounded px-2 py-1 text-xs hover:bg-accent/50"
                >
                  <Badge
                    variant="outline"
                    className={`text-[10px] ${NODE_COLORS[node.type]}`}
                  >
                    {node.type}
                  </Badge>
                  <span className="truncate font-mono text-[11px]">{node.label}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs">Relationships</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {graph.edges.slice(0, 50).map((edge, i) => (
                <div
                  key={i}
                  className="flex items-center gap-1 rounded px-2 py-1 text-[11px] hover:bg-accent/50"
                >
                  <span className="truncate font-mono">{edge.source.split(":").pop()}</span>
                  <Link2 className="h-2.5 w-2.5 shrink-0 text-muted-foreground" />
                  <Badge variant="outline" className="shrink-0 text-[9px]">
                    {edge.type}
                  </Badge>
                  <Link2 className="h-2.5 w-2.5 shrink-0 text-muted-foreground" />
                  <span className="truncate font-mono">{edge.target.split(":").pop()}</span>
                </div>
              ))}
              {graph.edges.length > 50 && (
                <p className="py-1 text-center text-[10px] text-muted-foreground">
                  + {graph.edges.length - 50} more edges
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </ScrollArea>
    </div>
  );
}
