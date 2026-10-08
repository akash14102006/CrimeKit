"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { ReactFlowProvider } from "@xyflow/react";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { useCaseKnowledgeGraph } from "@/hooks/queries/useKnowledgeGraph";
import { useGraphStore } from "../store/graphStore";
import { useGraphWebSocket } from "../hooks/useGraphWebSocket";
import { GraphToolbar } from "./GraphToolbar";
import { Graph3DViewer } from "./Graph3DViewer";
import { InteractiveGraph } from "./InteractiveGraph";
import { ForensicInspectorPanel } from "./ForensicInspectorPanel";
import { EdgeDetailsPanel } from "./EdgeDetailsPanel";
import { GraphGDSPanel } from "./GraphGDSPanel";
import { GraphLegend } from "./GraphLegend";
import { CaseAtlas } from "./CaseAtlas";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FolderLock, ArrowLeft } from "lucide-react";
import type { GraphNode, GraphEdge } from "@/types/kg";

interface Props {
  caseId?: string;
}

function GraphContent({ caseId }: { caseId: string }) {
  const { data: kgData, isLoading, refetch } = useCaseKnowledgeGraph(caseId);
  const {
    nodes: storeNodes,
    edges: storeEdges,
    selectedNodeId,
    selectedEdgeId,
    selectNode,
    selectEdge,
    viewMode,
    setGraphData,
    pendingEvents,
  } = useGraphStore();

  const [showGDSPanel, setShowGDSPanel] = useState<boolean>(false);
  const { isConnected: wsConnected } = useGraphWebSocket(caseId);

  // Parse API response and populate store
  const apiNodes = useMemo(() => {
    if (!kgData?.graph) return [];
    const graphData = kgData.graph as unknown;
    if (Array.isArray(graphData)) {
      return graphData.filter((n): n is GraphNode => n !== null && typeof n === "object" && "id" in n && "label" in n);
    }
    if (graphData && typeof graphData === "object" && "nodes" in graphData && Array.isArray((graphData as Record<string, unknown>).nodes)) {
      return (graphData as Record<string, unknown>).nodes as GraphNode[];
    }
    return [];
  }, [kgData]);

  const apiEdges = useMemo(() => {
    if (!kgData?.graph) return [];
    const graphData = kgData.graph as unknown;
    if (graphData && typeof graphData === "object" && "edges" in graphData && Array.isArray((graphData as Record<string, unknown>).edges)) {
      return (graphData as Record<string, unknown>).edges as GraphEdge[];
    }
    if (Array.isArray(graphData)) {
      const edges: GraphEdge[] = [];
      for (const item of graphData) {
        if (item && typeof item === "object" && "source" in item && "target" in item) {
          edges.push(item as GraphEdge);
        }
      }
      return edges;
    }
    return [];
  }, [kgData]);

  // Sync API data into store
  useEffect(() => {
    if (apiNodes.length > 0 || apiEdges.length > 0) {
      setGraphData(apiNodes, apiEdges);
    }
  }, [apiNodes, apiEdges, setGraphData]);

  // Use store data (includes both API and real-time updates)
  const allNodes = storeNodes.length > 0 ? storeNodes : apiNodes;
  const allEdges = storeEdges.length > 0 ? storeEdges : apiEdges;

  const selectedNode = useMemo(
    () => allNodes.find((n) => n.id === selectedNodeId) ?? null,
    [allNodes, selectedNodeId],
  );

  const selectedEdge = useMemo(
    () => allEdges.find((e) => e.id === selectedEdgeId) ?? null,
    [allEdges, selectedEdgeId],
  );

  const hasDetailPanel = Boolean(selectedNode || selectedEdge || showGDSPanel);

  return (
    <div className="flex flex-col h-full bg-background text-foreground">
      {/* Graph Toolbar */}
      <div className="px-3 py-1.5 border-b border-border bg-card/80 flex items-center justify-between">
        <GraphToolbar
          nodes={allNodes}
          edges={allEdges}
          isLoading={isLoading}
          onRefresh={() => refetch()}
          onZoomIn={() => {}}
          onZoomOut={() => {}}
          onFitView={() => {}}
          onToggleGDS={() => setShowGDSPanel((prev) => !prev)}
          showGDS={showGDSPanel}
          wsConnected={wsConnected}
        />
      </div>

      {/* Main Canvas + Inspector Resizable Layout */}
      <div className="flex-1 min-h-0 relative">
        <ResizablePanelGroup orientation="horizontal" className="h-full">
          {/* Main Visualization Panel */}
          <ResizablePanel defaultSize={hasDetailPanel ? 65 : 100} minSize={40}>
            {viewMode === "3d" ? (
              <Graph3DViewer
                nodes={allNodes}
                edges={allEdges}
                onNodeClick={(node) => selectNode(node.id)}
                onEdgeClick={(edge) => selectEdge(edge.id)}
                caseId={caseId}
              />
            ) : (
              <InteractiveGraph
                kgNodes={allNodes}
                kgEdges={allEdges}
                onNodeClick={(node) => selectNode(node.id)}
                onEdgeClick={(edge) => selectEdge(edge.id)}
              />
            )}
          </ResizablePanel>

          {/* Side Inspector / GDS Panel */}
          {hasDetailPanel && (
            <>
              <ResizableHandle withHandle className="bg-border" />
              <ResizablePanel defaultSize={35} minSize={25} collapsible collapsedSize={0}>
                {selectedNode ? (
                  <ForensicInspectorPanel
                    node={selectedNode}
                    allNodes={allNodes}
                    edges={allEdges}
                    onClose={() => selectNode(null)}
                    caseId={caseId}
                  />
                ) : selectedEdge ? (
                  <EdgeDetailsPanel
                    edge={selectedEdge}
                    allNodes={allNodes}
                    onClose={() => selectEdge(null)}
                  />
                ) : showGDSPanel ? (
                  <GraphGDSPanel
                    caseId={caseId}
                    nodes={allNodes}
                    edges={allEdges}
                    onClose={() => setShowGDSPanel(false)}
                  />
                ) : null}
              </ResizablePanel>
            </>
          )}
        </ResizablePanelGroup>
      </div>
    </div>
  );
}

export function GraphPage({ caseId: propCaseId }: Props = {}) {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();

  const activeCaseId =
    propCaseId ??
    (params?.caseId as string) ??
    searchParams?.get("case_id") ??
    undefined;

  const { setCaseId } = useGraphStore();

  useEffect(() => {
    setCaseId(activeCaseId ?? null);
  }, [activeCaseId, setCaseId]);

  const handleSelectCase = (id: string) => {
    setCaseId(id);
    router.push(`/knowledge-graph?case_id=${encodeURIComponent(id)}`);
  };

  const handleSwitchCase = () => {
    setCaseId(null);
    router.push("/knowledge-graph");
  };

  // Clean case display title (remove raw long UUIDs from display)
  const displayCaseName = activeCaseId
    ? activeCaseId.includes("case_core_")
      ? "Active Investigation"
      : activeCaseId.length > 20
      ? `Case #${activeCaseId.slice(0, 8)}...`
      : `Case: ${activeCaseId}`
    : null;

  return (
    <ReactFlowProvider>
      <div className="flex flex-col h-full bg-background text-foreground">
        {/* Minimal Header */}
        <div className="px-4 py-2 border-b border-border bg-card/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-base font-bold tracking-tight text-foreground flex items-center gap-2">
              <span>CrimeKit</span>
              <span className="text-muted-foreground font-normal">/</span>
              <span className="text-sky-500 font-semibold">Knowledge Graph</span>
            </h1>
            {displayCaseName && (
              <Badge variant="outline" className="text-xs font-mono bg-muted/60 border-border text-foreground">
                <FolderLock className="h-3 w-3 mr-1 text-sky-500" />
                {displayCaseName}
              </Badge>
            )}
          </div>

          {activeCaseId && (
            <Button
              variant="outline"
              size="sm"
              className="h-7 px-2.5 gap-1.5 border-border bg-card text-foreground hover:bg-accent text-xs"
              onClick={handleSwitchCase}
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Switch Case</span>
            </Button>
          )}
        </div>

        {activeCaseId ? (
          <div className="flex-1 min-h-0">
            <GraphContent caseId={activeCaseId} />
          </div>
        ) : (
          <CaseAtlas onSelectCase={handleSelectCase} />
        )}
      </div>
    </ReactFlowProvider>
  );
}
