"use client";

import { useMemo, useCallback } from "react";
import {
  ReactFlow,
  Background,
  MiniMap,
  Controls,
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
  type NodeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { CustomGraphNode } from "./GraphNode";
import { useGraphStore } from "../store/graphStore";
import type { GraphNode as KGNode, GraphEdge as KGEdge } from "@/types/kg";

const nodeTypes: NodeTypes = {
  graphNode: CustomGraphNode,
};

const NODE_TYPE_COLORS: Record<string, string> = {
  person: "#3b82f6",
  location: "#22c55e",
  device: "#a855f7",
  organization: "#f97316",
  evidence: "#10b981",
  url: "#06b6d4",
  process: "#6366f1",
  case: "#f59e0b",
  timeline: "#ec4899",
  entity: "#6b7280",
};

interface Props {
  kgNodes: KGNode[];
  kgEdges: KGEdge[];
  onNodeClick: (node: KGNode) => void;
  onEdgeClick: (edge: KGEdge) => void;
}

function applyForceLayout(nodes: KGNode[], edges: KGEdge[]): { nodes: Node[]; edges: Edge[] } {
  const adjacency: Record<string, string[]> = {};
  for (const n of nodes) adjacency[n.id] = [];
  for (const e of edges) {
    adjacency[e.source]?.push(e.target);
    adjacency[e.target]?.push(e.source);
  }

  const positions: Record<string, { x: number; y: number }> = {};
  const count = nodes.length;
  const radius = Math.max(200, count * 15);

  nodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / count;
    const layer = (adjacency[node.id]?.length ?? 0);
    const r = radius * (0.5 + Math.min(layer, 5) * 0.1);
    positions[node.id] = {
      x: 400 + r * Math.cos(angle),
      y: 300 + r * Math.sin(angle),
    };
  });

  const flowNodes: Node[] = nodes.map((n) => ({
    id: n.id,
    type: "graphNode",
    position: positions[n.id] ?? { x: 0, y: 0 },
    data: { label: n.label, type: n.type, properties: n.properties },
  }));

  const flowEdges: Edge[] = edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.label ?? e.type,
    type: "default",
    animated: false,
    style: { stroke: "#94a3b8", strokeWidth: 1.5 },
  }));

  return { nodes: flowNodes, edges: flowEdges };
}

export function InteractiveGraph({ kgNodes, kgEdges, onNodeClick, onEdgeClick }: Props) {
  const { searchQuery, nodeTypeFilter } = useGraphStore();

  const filteredNodes = useMemo(() => {
    let nodes = kgNodes;
    if (nodeTypeFilter && nodeTypeFilter !== "all") {
      nodes = nodes.filter((n) => (n.type ?? "entity").toLowerCase() === nodeTypeFilter);
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      nodes = nodes.filter(
        (n) =>
          n.label.toLowerCase().includes(q) ||
          n.id.toLowerCase().includes(q) ||
          n.type?.toLowerCase().includes(q),
      );
    }
    return nodes;
  }, [kgNodes, nodeTypeFilter, searchQuery]);

  const filteredEdges = useMemo(() => {
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    return kgEdges.filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target));
  }, [kgEdges, filteredNodes]);

  const { nodes: flowNodes, edges: flowEdges } = useMemo(
    () => applyForceLayout(filteredNodes, filteredEdges),
    [filteredNodes, filteredEdges],
  );

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const kgNode = kgNodes.find((n) => n.id === node.id);
      if (kgNode) onNodeClick(kgNode);
    },
    [kgNodes, onNodeClick],
  );

  const handleEdgeClick = useCallback(
    (_: React.MouseEvent, edge: Edge) => {
      const kgEdge = kgEdges.find((e) => e.id === edge.id);
      if (kgEdge) onEdgeClick(kgEdge);
    },
    [kgEdges, onEdgeClick],
  );

  const handleNodesChange = useCallback<OnNodesChange>(() => {}, []);
  const handleEdgesChange = useCallback<OnEdgesChange>(() => {}, []);

  if (flowNodes.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center space-y-3">
          <Network className="h-16 w-16 mx-auto text-muted-foreground opacity-40" />
          <p className="text-sm text-muted-foreground">No graph data available</p>
          <p className="text-xs text-muted-foreground">Ingest evidence into the Knowledge Graph to visualize relationships</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={4}
        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
      >
        <Background gap={20} size={1} />
        <Controls showInteractive={false} />
        <MiniMap
          nodeColor={(node) => {
            const t = (node.data?.type as string ?? "entity").toLowerCase();
            return NODE_TYPE_COLORS[t] ?? NODE_TYPE_COLORS.entity;
          }}
          maskColor="rgba(0,0,0,0.1)"
          style={{ width: 120, height: 80 }}
        />
      </ReactFlow>
    </div>
  );
}

function Network(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="16" y="16" width="6" height="6" rx="1" />
      <rect x="2" y="16" width="6" height="6" rx="1" />
      <rect x="9" y="2" width="6" height="6" rx="1" />
      <path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3" />
      <path d="M12 12V8" />
    </svg>
  );
}
