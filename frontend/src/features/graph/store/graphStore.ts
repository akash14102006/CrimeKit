import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { GraphNode, GraphEdge } from "@/types/kg";

export type GraphLayout = "force" | "hierarchical" | "circular" | "grid";

interface GraphState {
  caseId: string | null;
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  searchQuery: string;
  nodeTypeFilter: string;
  edgeTypeFilter: string;
  layout: GraphLayout;
  showAnalytics: boolean;
  showMiniMap: boolean;
  expandedNodes: Set<string>;

  // Graph data (from API + real-time updates)
  nodes: GraphNode[];
  edges: GraphEdge[];
  graphVersion: number;
  lastSyncedAt: number | null;
  isConnected: boolean;
  pendingEvents: number;
}

interface GraphActions {
  setCaseId: (caseId: string | null) => void;
  selectNode: (id: string | null) => void;
  selectEdge: (id: string | null) => void;
  setSearchQuery: (query: string) => void;
  setNodeTypeFilter: (filter: string) => void;
  setEdgeTypeFilter: (filter: string) => void;
  setLayout: (layout: GraphLayout) => void;
  toggleAnalytics: () => void;
  toggleMiniMap: () => void;
  expandNode: (id: string) => void;

  // Graph data mutations
  setGraphData: (nodes: GraphNode[], edges: GraphEdge[]) => void;
  addNode: (node: GraphNode) => void;
  addEdge: (edge: GraphEdge) => void;
  updateNode: (id: string, updates: Partial<GraphNode>) => void;
  updateEdge: (id: string, updates: Partial<GraphEdge>) => void;
  removeNode: (id: string) => void;
  removeEdge: (id: string) => void;
  setConnected: (connected: boolean) => void;
  incrementPendingEvents: () => void;
  clearPendingEvents: () => void;
  setGraphVersion: (version: number) => void;

  reset: () => void;
}

const initialState: GraphState = {
  caseId: null,
  selectedNodeId: null,
  selectedEdgeId: null,
  searchQuery: "",
  nodeTypeFilter: "all",
  edgeTypeFilter: "all",
  layout: "force",
  showAnalytics: false,
  showMiniMap: true,
  expandedNodes: new Set(),
  nodes: [],
  edges: [],
  graphVersion: 0,
  lastSyncedAt: null,
  isConnected: false,
  pendingEvents: 0,
};

export const useGraphStore = create<GraphState & GraphActions>()(
  persist(
    (set) => ({
      ...initialState,
      setCaseId: (caseId) =>
        set({
          ...initialState,
          caseId,
          nodes: [],
          edges: [],
          graphVersion: 0,
          lastSyncedAt: null,
        }),
      selectNode: (selectedNodeId) =>
        set({ selectedNodeId, selectedEdgeId: null }),
      selectEdge: (selectedEdgeId) =>
        set({ selectedEdgeId, selectedNodeId: null }),
      setSearchQuery: (searchQuery) => set({ searchQuery }),
      setNodeTypeFilter: (nodeTypeFilter) => set({ nodeTypeFilter }),
      setEdgeTypeFilter: (edgeTypeFilter) => set({ edgeTypeFilter }),
      setLayout: (layout) => set({ layout }),
      toggleAnalytics: () => set((s) => ({ showAnalytics: !s.showAnalytics })),
      toggleMiniMap: () => set((s) => ({ showMiniMap: !s.showMiniMap })),
      expandNode: (id) =>
        set((s) => ({
          expandedNodes: new Set([...s.expandedNodes, id]),
        })),

      // ── Graph data mutations ──
      setGraphData: (nodes, edges) =>
        set({
          nodes,
          edges,
          graphVersion: Date.now(),
          lastSyncedAt: Date.now(),
        }),

      addNode: (node) =>
        set((s) => {
          const exists = s.nodes.some((n) => n.id === node.id);
          if (exists) return s;
          return {
            nodes: [...s.nodes, node],
            graphVersion: Date.now(),
          };
        }),

      addEdge: (edge) =>
        set((s) => {
          const exists = s.edges.some(
            (e) => e.source === edge.source && e.target === edge.target && e.type === edge.type,
          );
          if (exists) return s;
          return {
            edges: [...s.edges, edge],
            graphVersion: Date.now(),
          };
        }),

      updateNode: (id, updates) =>
        set((s) => ({
          nodes: s.nodes.map((n) => (n.id === id ? { ...n, ...updates } : n)),
          graphVersion: Date.now(),
        })),

      updateEdge: (id, updates) =>
        set((s) => ({
          edges: s.edges.map((e) => (e.id === id ? { ...e, ...updates } : e)),
          graphVersion: Date.now(),
        })),

      removeNode: (id) =>
        set((s) => ({
          nodes: s.nodes.filter((n) => n.id !== id),
          edges: s.edges.filter((e) => e.source !== id && e.target !== id),
          selectedNodeId: s.selectedNodeId === id ? null : s.selectedNodeId,
          graphVersion: Date.now(),
        })),

      removeEdge: (id) =>
        set((s) => ({
          edges: s.edges.filter((e) => e.id !== id),
          selectedEdgeId: s.selectedEdgeId === id ? null : s.selectedEdgeId,
          graphVersion: Date.now(),
        })),

      setConnected: (isConnected) => set({ isConnected }),
      incrementPendingEvents: () =>
        set((s) => ({ pendingEvents: s.pendingEvents + 1 })),
      clearPendingEvents: () => set({ pendingEvents: 0 }),
      setGraphVersion: (graphVersion) => set({ graphVersion }),

      reset: () => set(initialState),
    }),
    {
      name: "crimekit-graph",
      partialize: (state) => ({
        layout: state.layout,
        showMiniMap: state.showMiniMap,
      }),
    },
  ),
);
