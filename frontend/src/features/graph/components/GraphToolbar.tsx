"use client";

import { useTheme } from "next-themes";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Search,
  X,
  LayoutGrid,
  Network,
  Circle,
  Box,
  RefreshCw,
  Download,
  ZoomIn,
  ZoomOut,
  Maximize,
  BoxSelect,
  Layers,
  ShieldCheck,
  BrainCircuit,
} from "lucide-react";
import { useGraphStore, type GraphLayout } from "../store/graphStore";
import { exportGraphToJSON, downloadFile } from "../lib/export";
import type { GraphNode, GraphEdge, FactClassification } from "@/types/kg";
import { GraphLegend } from "./GraphLegend";

const LAYOUT_OPTIONS: { value: GraphLayout; label: string; icon: typeof LayoutGrid }[] = [
  { value: "force", label: "Force Directed", icon: Network },
  { value: "hierarchical", label: "Hierarchical", icon: LayoutGrid },
  { value: "circular", label: "Circular", icon: Circle },
  { value: "grid", label: "Grid", icon: Box },
];

const NODE_TYPE_FILTERS = [
  { value: "all", label: "All Types" },
  { value: "person", label: "Person" },
  { value: "location", label: "Location" },
  { value: "device", label: "Device" },
  { value: "organization", label: "Organization" },
  { value: "evidence", label: "Evidence" },
  { value: "url", label: "URL" },
  { value: "process", label: "Process" },
  { value: "case", label: "Case" },
  { value: "entity", label: "Entity" },
];

const FACT_FILTERS: { value: FactClassification | "ALL"; label: string }[] = [
  { value: "ALL", label: "All Facts" },
  { value: "OBSERVED", label: "Observed Facts" },
  { value: "DERIVED", label: "Derived Inferences" },
  { value: "HYPOTHESIS", label: "Hypotheses" },
  { value: "CANDIDATE", label: "Candidates" },
  { value: "REVIEWED", label: "Reviewed" },
];

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
  isLoading: boolean;
  onRefresh: () => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
  onToggleGDS?: () => void;
  showGDS?: boolean;
  wsConnected?: boolean;
}

export function GraphToolbar({
  nodes,
  edges,
  isLoading,
  onRefresh,
  onZoomIn,
  onZoomOut,
  onFitView,
  onToggleGDS,
  showGDS,
  wsConnected = true,
}: Props) {
  const { resolvedTheme } = useTheme();

  const {
    searchQuery,
    setSearchQuery,
    nodeTypeFilter,
    setNodeTypeFilter,
    factClassificationFilter,
    setFactClassificationFilter,
    viewMode,
    setViewMode,
    layout,
    setLayout,
  } = useGraphStore();

  const handleExportJSON = () => {
    const json = exportGraphToJSON(nodes, edges);
    downloadFile(json, `graph-export-${new Date().toISOString().slice(0, 10)}.json`, "application/json");
  };

  return (
    <div className="flex items-center gap-2 flex-wrap text-foreground w-full">
      {/* 3D / 2D View Mode Switcher */}
      <div className="flex items-center p-0.5 rounded-lg border border-border bg-muted/80 text-xs">
        <Button
          variant={viewMode === "3d" ? "default" : "ghost"}
          size="sm"
          className={`h-7 px-2 text-xs font-semibold gap-1 ${viewMode === "3d" ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"}`}
          onClick={() => setViewMode("3d")}
        >
          <BoxSelect className="h-3.5 w-3.5" />
          3D
        </Button>
        <Button
          variant={viewMode === "2d" ? "default" : "ghost"}
          size="sm"
          className={`h-7 px-2 text-xs font-semibold gap-1 ${viewMode === "2d" ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"}`}
          onClick={() => setViewMode("2d")}
        >
          <Layers className="h-3.5 w-3.5" />
          2D
        </Button>
      </div>

      {/* Search Input */}
      <div className="relative flex-1 min-w-[160px] max-w-xs">
        <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground" />
        <Input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Filter graph entities..."
          className="h-7 pl-8 pr-7 text-xs bg-background border-border text-foreground placeholder:text-muted-foreground"
        />
        {searchQuery && (
          <Button variant="ghost" size="sm" className="absolute right-1 top-0.5 h-6 w-6 p-0 text-muted-foreground hover:text-foreground" onClick={() => setSearchQuery("")}>
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>

      {/* Fact Classification Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger className="inline-flex items-center gap-1 h-7 px-2 text-xs font-medium rounded border border-border bg-background hover:bg-muted text-foreground">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
          <span>{FACT_FILTERS.find((f) => f.value === factClassificationFilter)?.label}</span>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="bg-popover border-border text-popover-foreground">
          {FACT_FILTERS.map((filter) => (
            <DropdownMenuItem key={filter.value} onClick={() => setFactClassificationFilter(filter.value)} className="hover:bg-muted text-xs">
              {filter.label}
              {factClassificationFilter === filter.value && <Badge variant="secondary" className="ml-auto text-[10px]">Active</Badge>}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Entity Type Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger className="inline-flex items-center gap-1 h-7 px-2 text-xs font-medium rounded border border-border bg-background hover:bg-muted text-foreground">
          <span>Type: {NODE_TYPE_FILTERS.find((f) => f.value === nodeTypeFilter)?.label}</span>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="bg-popover border-border text-popover-foreground">
          {NODE_TYPE_FILTERS.map((filter) => (
            <DropdownMenuItem key={filter.value} onClick={() => setNodeTypeFilter(filter.value)} className="hover:bg-muted text-xs">
              {filter.label}
              {nodeTypeFilter === filter.value && <Badge variant="secondary" className="ml-auto text-[10px]">Active</Badge>}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Graph Legend Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger className="inline-flex items-center gap-1 h-7 px-2 text-xs font-medium rounded border border-border bg-background hover:bg-muted text-foreground">
          <Circle className="h-3 w-3 text-sky-500 fill-sky-500" />
          <span>Legend</span>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="p-3 bg-popover border-border text-popover-foreground w-64">
          <div className="text-xs font-semibold mb-2 border-b border-border pb-1">Entity Categories</div>
          <GraphLegend />
        </DropdownMenuContent>
      </DropdownMenu>

      {/* GDS Analytics Toggle */}
      {onToggleGDS && (
        <Button
          variant={showGDS ? "default" : "outline"}
          size="sm"
          className={`h-7 px-2.5 gap-1.5 text-xs ${showGDS ? "bg-primary text-primary-foreground" : "border-border bg-background text-foreground hover:bg-muted"}`}
          onClick={onToggleGDS}
        >
          <BrainCircuit className="h-3.5 w-3.5 text-sky-500" />
          <span>GDS</span>
        </Button>
      )}

      {/* Refresh */}
      <Button variant="outline" size="sm" className="h-7 w-7 p-0 border-border bg-background text-foreground hover:bg-muted" onClick={onRefresh} disabled={isLoading} title="Refresh graph data">
        <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
      </Button>

      {/* Export */}
      <Button variant="outline" size="sm" className="h-7 px-2 gap-1 border-border bg-background text-foreground hover:bg-muted text-xs" onClick={handleExportJSON}>
        <Download className="h-3.5 w-3.5" />
        <span>Export</span>
      </Button>

      <div className="flex-1" />

      {/* Minimal Status Indicator & Clean Counters */}
      <div className="flex items-center gap-2">
        <div
          className={`h-2 w-2 rounded-full ${wsConnected ? "bg-emerald-500 shadow-sm shadow-emerald-500 animate-pulse" : "bg-muted-foreground"}`}
          title={wsConnected ? "Real-time Graph Stream Active" : "Offline"}
        />
        <span className="text-xs font-mono text-muted-foreground">
          {nodes.length} nodes &middot; {edges.length} links
        </span>
      </div>
    </div>
  );
}
