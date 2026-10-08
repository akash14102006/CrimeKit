"use client";

import React, { useState } from "react";
import dynamic from "next/dynamic";
import { useTheme } from "next-themes";
import { useGraphStore } from "../store/graphStore";
import type { GraphNode, GraphEdge } from "@/types/kg";
import { ForensicTracePanel } from "./ForensicTracePanel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Zap, Activity } from "lucide-react";

// Dynamically import Forensic3DScene without SSR
const Forensic3DScene = dynamic(
  () => import("./Forensic3DScene").then((m) => m.Forensic3DScene),
  { ssr: false }
);

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  caseId?: string;
}

export function Graph3DViewer({ nodes, edges, onNodeClick, onEdgeClick, caseId }: Props) {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme !== "light";

  const {
    selectedNodeId,
    focusedNodeId,
    selectNode,
    minConfidence,
    factClassificationFilter,
    nodeTypeFilter,
    searchQuery,
    isConnected: wsConnected,
    pendingEvents,
  } = useGraphStore();

  const [showTracePanel, setShowTracePanel] = useState<boolean>(true);

  const hudBg = isDark
    ? "bg-slate-950/80 border-slate-800 text-slate-200"
    : "bg-white/90 border-slate-200 text-slate-800 shadow-md";

  return (
    <div className={`relative w-full h-full overflow-hidden select-none ${isDark ? "bg-[#05070d]" : "bg-slate-50"}`}>
      {/* Minimal Top-Left Controls */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2">
        <Button
          variant={showTracePanel ? "default" : "outline"}
          size="sm"
          className={`h-7 px-2.5 text-xs gap-1.5 backdrop-blur-md shadow-md ${showTracePanel ? "bg-sky-600 text-white hover:bg-sky-700" : isDark ? "bg-slate-900/80 border-slate-800 text-slate-300 hover:text-white" : "bg-white/90 border-slate-200 text-slate-700 hover:text-slate-900"}`}
          onClick={() => setShowTracePanel((prev) => !prev)}
        >
          <Activity className="h-3.5 w-3.5" />
          <span>Activity Log</span>
        </Button>
      </div>

      {/* Forensic Trace Floating Panel */}
      {showTracePanel && (
        <ForensicTracePanel
          caseId={caseId || "default"}
          wsConnected={wsConnected}
          pendingEvents={pendingEvents}
          isDark={isDark}
          onClose={() => setShowTracePanel(false)}
        />
      )}

      {/* R3F WebGL 3D Scene */}
      <Forensic3DScene
        nodes={nodes}
        edges={edges}
        caseId={caseId}
        selectedNodeId={selectedNodeId}
        focusedNodeId={focusedNodeId}
        minConfidence={minConfidence}
        factClassificationFilter={factClassificationFilter}
        nodeTypeFilter={nodeTypeFilter}
        searchQuery={searchQuery}
        isDark={isDark}
        onNodeClick={(node) => {
          selectNode(node.id);
          if (onNodeClick) onNodeClick(node);
        }}
        onEdgeClick={(edge) => {
          if (onEdgeClick) onEdgeClick(edge);
        }}
      />
    </div>
  );
}
