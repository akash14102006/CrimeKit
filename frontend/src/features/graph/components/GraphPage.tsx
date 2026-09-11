"use client";

import { useEffect, useMemo } from "react";
import { useParams } from "next/navigation";
import { ReactFlowProvider } from "@xyflow/react";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { useCaseKnowledgeGraph } from "@/hooks/queries/useKnowledgeGraph";
import { useGraphStore } from "../store/graphStore";
import { useGraphWebSocket } from "../hooks/useGraphWebSocket";
import { GraphToolbar } from "./GraphToolbar";
import { InteractiveGraph } from "./InteractiveGraph";
import { NodeDetailsPanel } from "./NodeDetailsPanel";
import { EdgeDetailsPanel } from "./EdgeDetailsPanel";
import { GraphLegend } from "./GraphLegend";
import { GraphAnalytics } from "./GraphAnalytics";
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
    showAnalytics,
    setGraphData,
    pendingEvents,
  } = useGraphStore();

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

  // Sync API data into store (only when store is empty or API data is newer)
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

  const hasDetail = selectedNode || selectedEdge;

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-2 border-b">
        <GraphToolbar
          nodes={allNodes}
          edges={allEdges}
          isLoading={isLoading}
          onRefresh={() => refetch()}
          onZoomIn={() => {}}
          onZoomOut={() => {}}
          onFitView={() => {}}
        />
        {/* Connection status indicator */}
        <div className="flex items-center gap-2 mt-1 text-xs">
          <div className={`h-2 w-2 rounded-full ${wsConnected ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-muted-foreground">
            {wsConnected ? "Live" : "Disconnected"}
          </span>
          {pendingEvents > 0 && (
            <span className="text-muted-foreground">({pendingEvents} events)</span>
          )}
        </div>
      </div>

      <div className="px-4 py-1.5 border-b">
        <GraphLegend />
      </div>

      <div className="flex-1 min-h-0">
        <ResizablePanelGroup orientation="horizontal" className="h-full">
          <ResizablePanel defaultSize={hasDetail ? 50 : showAnalytics ? 65 : 100} minSize={30}>
            <InteractiveGraph
              kgNodes={allNodes}
              kgEdges={allEdges}
              onNodeClick={(node) => selectNode(node.id)}
              onEdgeClick={(edge) => selectEdge(edge.id)}
            />
          </ResizablePanel>

          {showAnalytics && (
            <>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={20} minSize={15} collapsible collapsedSize={0}>
                <GraphAnalytics nodes={allNodes} edges={allEdges} />
              </ResizablePanel>
            </>
          )}

          {hasDetail && (
            <>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={30} minSize={20} collapsible collapsedSize={0}>
                {selectedNode ? (
                  <NodeDetailsPanel
                    node={selectedNode}
                    edges={allEdges}
                    allNodes={allNodes}
                    onClose={() => selectNode(null)}
                    isLoading={isLoading}
                  />
                ) : selectedEdge ? (
                  <EdgeDetailsPanel
                    edge={selectedEdge}
                    allNodes={allNodes}
                    onClose={() => selectEdge(null)}
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
  const caseId = propCaseId ?? (params?.caseId as string);
  const { setCaseId } = useGraphStore();

  useEffect(() => {
    setCaseId(caseId ?? null);
  }, [caseId, setCaseId]);

  return (
    <ReactFlowProvider>
      <div className="flex flex-col h-full">
        <div className="px-4 py-3 border-b">
          <h1 className="text-2xl font-bold tracking-tight">Knowledge Graph</h1>
          <p className="text-sm text-muted-foreground">
            {caseId ? `Case-scoped entity relationship visualization` : `Select a case to view its knowledge graph`}
          </p>
        </div>

        {caseId ? (
          <div className="flex-1 min-h-0">
            <GraphContent caseId={caseId} />
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-3">
              <Network className="h-12 w-12 mx-auto text-muted-foreground opacity-40" />
              <p className="text-sm font-medium">No case selected</p>
              <p className="text-xs text-muted-foreground">Navigate to a case workspace to view its knowledge graph</p>
            </div>
          </div>
        )}
      </div>
    </ReactFlowProvider>
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
