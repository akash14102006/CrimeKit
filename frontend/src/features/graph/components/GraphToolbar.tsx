"use client";

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
  BarChart3,
  Map,
  RefreshCw,
  Download,
  ZoomIn,
  ZoomOut,
  Maximize,
} from "lucide-react";
import { useGraphStore, type GraphLayout } from "../store/graphStore";
import { exportGraphToJSON, downloadFile } from "../lib/export";
import type { GraphNode, GraphEdge } from "@/types/kg";

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

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
  isLoading: boolean;
  onRefresh: () => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
}

export function GraphToolbar({ nodes, edges, isLoading, onRefresh, onZoomIn, onZoomOut, onFitView }: Props) {
  const {
    searchQuery, setSearchQuery,
    nodeTypeFilter, setNodeTypeFilter,
    layout, setLayout,
    showAnalytics, toggleAnalytics,
    showMiniMap, toggleMiniMap,
  } = useGraphStore();

  const handleExportJSON = () => {
    const json = exportGraphToJSON(nodes, edges);
    downloadFile(json, `graph-export-${new Date().toISOString().slice(0, 10)}.json`, "application/json");
  };

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <div className="relative flex-1 min-w-[200px] max-w-md">
        <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
        <Input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search entities..."
          className="h-8 pl-8 pr-8 text-xs"
        />
        {searchQuery && (
          <Button variant="ghost" size="sm" className="absolute right-1 top-1 h-6 w-6 p-0" onClick={() => setSearchQuery("")}>
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>

      <div className="flex items-center gap-1 border rounded-md">
        <Button variant="ghost" size="sm" className="h-7 px-2" onClick={onZoomIn}>
          <ZoomIn className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className="h-7 px-2" onClick={onZoomOut}>
          <ZoomOut className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className="h-7 px-2" onClick={onFitView}>
          <Maximize className="h-3.5 w-3.5" />
        </Button>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger className="inline-flex items-center gap-1 h-7 px-2 text-xs font-medium rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground">
          <LayoutGrid className="h-3 w-3" />
          {LAYOUT_OPTIONS.find((l) => l.value === layout)?.label}
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          {LAYOUT_OPTIONS.map((opt) => {
            const Icon = opt.icon;
            return (
              <DropdownMenuItem key={opt.value} onClick={() => setLayout(opt.value)}>
                <Icon className="h-3.5 w-3.5 mr-2" />
                {opt.label}
                {layout === opt.value && <Badge variant="secondary" className="ml-2 text-[10px]">Active</Badge>}
              </DropdownMenuItem>
            );
          })}
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger className="inline-flex items-center gap-1 h-7 px-2 text-xs font-medium rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground">
          Filter: {NODE_TYPE_FILTERS.find((f) => f.value === nodeTypeFilter)?.label}
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          {NODE_TYPE_FILTERS.map((filter) => (
            <DropdownMenuItem key={filter.value} onClick={() => setNodeTypeFilter(filter.value)}>
              {filter.label}
              {nodeTypeFilter === filter.value && <Badge variant="secondary" className="ml-2 text-[10px]">Active</Badge>}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <Button variant={showAnalytics ? "default" : "outline"} size="sm" className="h-7 gap-1" onClick={toggleAnalytics}>
        <BarChart3 className="h-3 w-3" />
        Analytics
      </Button>

      <Button variant={showMiniMap ? "default" : "outline"} size="sm" className="h-7 gap-1" onClick={toggleMiniMap}>
        <Map className="h-3 w-3" />
      </Button>

      <Button variant="outline" size="sm" className="h-7" onClick={onRefresh} disabled={isLoading}>
        <RefreshCw className={`h-3 w-3 ${isLoading ? "animate-spin" : ""}`} />
      </Button>

      <Button variant="outline" size="sm" className="h-7 gap-1" onClick={handleExportJSON}>
        <Download className="h-3 w-3" />
        Export
      </Button>

      <div className="flex-1" />

      <Badge variant="outline" className="text-[10px]">
        {nodes.length} nodes &middot; {edges.length} edges
      </Badge>
    </div>
  );
}
