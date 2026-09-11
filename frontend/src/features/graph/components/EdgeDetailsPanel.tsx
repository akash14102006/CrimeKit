"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X, ArrowRight, GitBranch } from "lucide-react";
import type { GraphNode, GraphEdge } from "@/types/kg";

interface Props {
  edge: GraphEdge | null;
  allNodes: GraphNode[];
  onClose: () => void;
}

export function EdgeDetailsPanel({ edge, allNodes, onClose }: Props) {
  if (!edge) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <div className="text-center space-y-2">
          <GitBranch className="h-10 w-10 mx-auto text-muted-foreground opacity-40" />
          <p className="text-xs text-muted-foreground">Select an edge to view details</p>
        </div>
      </div>
    );
  }

  const sourceNode = allNodes.find((n) => n.id === edge.source);
  const targetNode = allNodes.find((n) => n.id === edge.target);
  const meta = (edge.properties ?? {}) as Record<string, unknown>;

  // Helper to safely extract string values from meta
  const metaStr = (key: string): string => String(meta[key] ?? "");
  const metaNum = (key: string): number => Number(meta[key] || 0);
  const metaBool = (key: string): boolean => Boolean(meta[key]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b">
        <div className="flex items-center gap-2 min-w-0">
          <GitBranch className="h-4 w-4 text-muted-foreground shrink-0" />
          <span className="font-medium text-sm truncate">Relationship Details</span>
        </div>
        <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={onClose}>
          <X className="h-3 w-3" />
        </Button>
      </div>

      <ScrollArea className="flex-1 p-4 space-y-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs">
            <Badge variant="outline" className="text-[10px]">{edge.type ?? "related"}</Badge>
          </div>

          <div className="flex items-center gap-2 text-xs p-2 bg-muted rounded">
            <span className="font-medium truncate">{sourceNode?.label ?? edge.source}</span>
            <ArrowRight className="h-3 w-3 shrink-0 text-muted-foreground" />
            <span className="font-medium truncate">{targetNode?.label ?? edge.target}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="space-y-1">
            <span className="text-muted-foreground">Source</span>
            <p className="font-medium truncate">{sourceNode?.label ?? "Unknown"}</p>
            <p className="text-[10px] font-mono text-muted-foreground truncate">{edge.source}</p>
          </div>
          <div className="space-y-1">
            <span className="text-muted-foreground">Target</span>
            <p className="font-medium truncate">{targetNode?.label ?? "Unknown"}</p>
            <p className="text-[10px] font-mono text-muted-foreground truncate">{edge.target}</p>
          </div>
        </div>

        {edge.label && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Label</span>
            <p className="text-xs font-medium">{edge.label}</p>
          </div>
        )}

        <div className="space-y-1">
          <span className="text-xs text-muted-foreground">Edge ID</span>
          <p className="text-[10px] font-mono break-all bg-muted p-2 rounded">{edge.id}</p>
        </div>

        {/* Evidence Provenance */}
        {typeof meta.confidence === "number" && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Confidence</span>
            <div className="flex items-center gap-2">
              <div className="h-1.5 flex-1 bg-muted rounded overflow-hidden">
                <div
                  className="h-full bg-primary"
                  style={{ width: `${Math.min(100, metaNum("confidence") * 100)}%` }}
                />
              </div>
              <span className="text-[10px] font-medium">{(metaNum("confidence") * 100).toFixed(0)}%</span>
            </div>
          </div>
        )}

        {typeof meta.evidence_id === "string" && meta.evidence_id && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Source Evidence</span>
            <p className="text-[10px] font-mono break-all bg-muted p-2 rounded">{metaStr("evidence_id")}</p>
          </div>
        )}

        {typeof meta.source_text === "string" && meta.source_text && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Source Text</span>
            <p className="text-[10px] italic bg-muted p-2 rounded">&ldquo;{metaStr("source_text")}&rdquo;</p>
          </div>
        )}

        {typeof meta.detected_at === "string" && meta.detected_at && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Detected</span>
            <p className="text-[10px]">{new Date(metaStr("detected_at")).toLocaleString()}</p>
          </div>
        )}

        {metaBool("is_new") && (
          <Badge className="text-[10px] bg-green-500/10 text-green-700 border-green-200">New</Badge>
        )}

        {Object.keys(meta).length > 0 && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Metadata</span>
            <div className="bg-muted p-2 rounded text-[10px] font-mono space-y-0.5">
              {Object.entries(meta).map(([key, value]) => (
                <div key={key} className="flex gap-2">
                  <span className="text-muted-foreground">{key}:</span>
                  <span className="truncate">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
