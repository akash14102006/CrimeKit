"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { GitBranch, ExternalLink, Circle } from "lucide-react";
import { useCaseKnowledgeGraph } from "@/hooks/queries/useKnowledgeGraph";

const NODE_COLORS: Record<string, string> = {
  PERSON: "bg-blue-100 text-blue-700",
  PHONE: "bg-green-100 text-green-700",
  EMAIL: "bg-purple-100 text-purple-700",
  DEVICE: "bg-amber-100 text-amber-700",
  ACCOUNT: "bg-pink-100 text-pink-700",
  LOCATION: "bg-red-100 text-red-700",
  ORGANIZATION: "bg-indigo-100 text-indigo-700",
  URL: "bg-cyan-100 text-cyan-700",
  IP_ADDRESS: "bg-orange-100 text-orange-700",
};

export function GraphReferencesPanel({ caseId }: { caseId: string }) {
  const { data: graph, isLoading } = useCaseKnowledgeGraph(caseId);

  const nodes: Array<{
    id: string;
    name: string;
    type: string;
  }> = [];

  if (graph && typeof graph === "object") {
    const graphData = graph as { graph?: Array<{ name?: string; type?: string; id?: string }> };
    if (Array.isArray(graphData.graph)) {
      for (const node of graphData.graph) {
        if (node && node.name) {
          nodes.push({
            id: node.id || node.name,
            name: node.name,
            type: node.type || "unknown",
          });
        }
      }
    }
  }

  const uniqueTypes = [...new Set(nodes.map((n) => n.type))];

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-semibold">KG References</h3>
          {nodes.length > 0 && (
            <Badge variant="secondary" className="text-[10px]">
              {nodes.length}
            </Badge>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-7 text-xs gap-1"
          onClick={() => window.open("/graph", "_blank")}
        >
          Open Graph
          <ExternalLink className="h-3 w-3" />
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {nodes.length === 0 ? (
            <div className="text-center py-12">
              <GitBranch className="h-12 w-12 mx-auto text-muted-foreground/20 mb-3" />
              <h4 className="text-sm font-medium mb-1">No Graph Data</h4>
              <p className="text-xs text-muted-foreground max-w-xs mx-auto">
                Ingest evidence into the knowledge graph to visualize entity
                relationships.
              </p>
            </div>
          ) : (
            <>
              {uniqueTypes.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {uniqueTypes.map((type) => (
                    <Badge
                      key={type}
                      variant="outline"
                      className={`text-[10px] ${NODE_COLORS[type] ?? "bg-gray-100 text-gray-700"}`}
                    >
                      {type}
                    </Badge>
                  ))}
                </div>
              )}

              {nodes.slice(0, 30).map((node) => (
                <div
                  key={node.id}
                  className="flex items-center gap-2 p-2 rounded-md hover:bg-muted/30 transition-colors"
                >
                  <Circle
                    className="h-2.5 w-2.5 fill-current shrink-0"
                    style={{
                      color: NODE_COLORS[node.type]
                        ? undefined
                        : "#9CA3AF",
                    }}
                  />
                  <div className="flex-1 min-w-0">
                    <span className="text-xs font-medium truncate block">
                      {node.name}
                    </span>
                  </div>
                  <Badge
                    variant="outline"
                    className={`text-[9px] ${NODE_COLORS[node.type] ?? ""}`}
                  >
                    {node.type}
                  </Badge>
                </div>
              ))}

              {nodes.length > 30 && (
                <p className="text-[10px] text-muted-foreground text-center">
                  +{nodes.length - 30} more entities
                </p>
              )}
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
