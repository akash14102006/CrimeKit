"use client";

import { useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { BarChart3 } from "lucide-react";
import type { GraphNode, GraphEdge } from "@/types/kg";

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export function GraphAnalytics({ nodes, edges }: Props) {
  const stats = useMemo(() => {
    const typeCounts: Record<string, number> = {};
    for (const node of nodes) {
      const t = (node.type ?? "entity").toLowerCase();
      typeCounts[t] = (typeCounts[t] || 0) + 1;
    }

    const edgeTypeCounts: Record<string, number> = {};
    for (const edge of edges) {
      const t = (edge.type ?? "related").toLowerCase();
      edgeTypeCounts[t] = (edgeTypeCounts[t] || 0) + 1;
    }

    const degreeMap: Record<string, number> = {};
    for (const edge of edges) {
      degreeMap[edge.source] = (degreeMap[edge.source] || 0) + 1;
      degreeMap[edge.target] = (degreeMap[edge.target] || 0) + 1;
    }

    const sortedDegrees = Object.entries(degreeMap).sort((a, b) => b[1] - a[1]);
    const mostConnected = sortedDegrees.length > 0 ? sortedDegrees[0] : null;

    const adjacency: Record<string, Set<string>> = {};
    for (const node of nodes) adjacency[node.id] = new Set();
    for (const edge of edges) {
      adjacency[edge.source]?.add(edge.target);
      adjacency[edge.target]?.add(edge.source);
    }
    let components = 0;
    const visited = new Set<string>();
    for (const node of nodes) {
      if (!visited.has(node.id)) {
        components++;
        const queue = [node.id];
        while (queue.length > 0) {
          const current = queue.shift()!;
          if (visited.has(current)) continue;
          visited.add(current);
          for (const neighbor of adjacency[current] ?? []) {
            if (!visited.has(neighbor)) queue.push(neighbor);
          }
        }
      }
    }

    const density = nodes.length > 1 ? edges.length / (nodes.length * (nodes.length - 1)) : 0;

    return {
      nodeCount: nodes.length,
      edgeCount: edges.length,
      typeCounts,
      edgeTypeCounts,
      mostConnected,
      connectedComponents: components,
      density: (density * 100).toFixed(2),
    };
  }, [nodes, edges]);

  return (
    <ScrollArea className="h-full">
      <div className="p-3 space-y-4">
        <h4 className="text-xs font-semibold flex items-center gap-1.5">
          <BarChart3 className="h-3.5 w-3.5" />
          Graph Analytics
        </h4>

        <div className="grid grid-cols-2 gap-2 text-center text-[10px]">
          <div className="p-2 rounded bg-muted/50">
            <p className="font-medium text-foreground">{stats.nodeCount}</p>
            <p className="text-muted-foreground">Nodes</p>
          </div>
          <div className="p-2 rounded bg-muted/50">
            <p className="font-medium text-foreground">{stats.edgeCount}</p>
            <p className="text-muted-foreground">Edges</p>
          </div>
          <div className="p-2 rounded bg-muted/50">
            <p className="font-medium text-foreground">{stats.connectedComponents}</p>
            <p className="text-muted-foreground">Components</p>
          </div>
          <div className="p-2 rounded bg-muted/50">
            <p className="font-medium text-foreground">{stats.density}%</p>
            <p className="text-muted-foreground">Density</p>
          </div>
        </div>

        {stats.mostConnected && (
          <div className="space-y-1">
            <span className="text-[10px] font-medium text-muted-foreground uppercase">Most Connected</span>
            <div className="p-2 rounded bg-muted/50 text-[10px]">
              <p className="font-medium">{stats.mostConnected[0]}</p>
              <p className="text-muted-foreground">{stats.mostConnected[1]} connections</p>
            </div>
          </div>
        )}

        {Object.keys(stats.typeCounts).length > 0 && (
          <div className="space-y-1">
            <span className="text-[10px] font-medium text-muted-foreground uppercase">Node Types</span>
            <div className="space-y-1">
              {Object.entries(stats.typeCounts)
                .sort((a, b) => b[1] - a[1])
                .map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between text-[10px]">
                    <span className="capitalize">{type}</span>
                    <Badge variant="outline" className="text-[9px]">{count}</Badge>
                  </div>
                ))}
            </div>
          </div>
        )}

        {Object.keys(stats.edgeTypeCounts).length > 0 && (
          <div className="space-y-1">
            <span className="text-[10px] font-medium text-muted-foreground uppercase">Edge Types</span>
            <div className="space-y-1">
              {Object.entries(stats.edgeTypeCounts)
                .sort((a, b) => b[1] - a[1])
                .map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between text-[10px]">
                    <span className="capitalize">{type}</span>
                    <Badge variant="outline" className="text-[9px]">{count}</Badge>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
