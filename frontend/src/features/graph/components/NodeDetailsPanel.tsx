"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  X,
  Users,
  MapPin,
  Smartphone,
  Building,
  FileText,
  Globe,
  Cpu,
  Shield,
  Clock,
  Database,
  GitBranch,
} from "lucide-react";
import type { GraphNode, GraphEdge } from "@/types/kg";

const TYPE_CONFIG: Record<string, { icon: typeof Users; color: string; label: string }> = {
  person: { icon: Users, color: "text-blue-600", label: "Person" },
  location: { icon: MapPin, color: "text-green-600", label: "Location" },
  device: { icon: Smartphone, color: "text-purple-600", label: "Device" },
  organization: { icon: Building, color: "text-orange-600", label: "Organization" },
  evidence: { icon: FileText, color: "text-emerald-600", label: "Evidence" },
  url: { icon: Globe, color: "text-cyan-600", label: "URL" },
  process: { icon: Cpu, color: "text-indigo-600", label: "Process" },
  case: { icon: Shield, color: "text-amber-600", label: "Case" },
  timeline: { icon: Clock, color: "text-pink-600", label: "Timeline" },
  entity: { icon: Database, color: "text-gray-600", label: "Entity" },
};

interface Props {
  node: GraphNode | null;
  edges: GraphEdge[];
  allNodes: GraphNode[];
  onClose: () => void;
  isLoading: boolean;
}

export function NodeDetailsPanel({ node, edges, allNodes, onClose, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="p-4 space-y-3">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }

  if (!node) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <div className="text-center space-y-2">
          <Database className="h-10 w-10 mx-auto text-muted-foreground opacity-40" />
          <p className="text-xs text-muted-foreground">Select a node to view details</p>
        </div>
      </div>
    );
  }

  const nodeType = (node.type ?? "entity").toLowerCase();
  const config = TYPE_CONFIG[nodeType] ?? TYPE_CONFIG.entity;
  const Icon = config.icon;
  const meta = (node.properties ?? {}) as Record<string, unknown>;

  // Helper to safely extract string values from meta
  const metaStr = (key: string): string => String(meta[key] ?? "");
  const metaBool = (key: string): boolean => Boolean(meta[key]);
  const metaNum = (key: string): number => Number(meta[key] || 0);

  const connectedEdges = edges.filter((e) => e.source === node.id || e.target === node.id);
  const connectedNodeIds = new Set(
    connectedEdges.flatMap((e) => [e.source, e.target]).filter((id) => id !== node.id),
  );
  const connectedNodes = allNodes.filter((n) => connectedNodeIds.has(n.id));

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b">
        <div className="flex items-center gap-2 min-w-0">
          <Icon className={`h-4 w-4 shrink-0 ${config.color}`} />
          <span className="font-medium text-sm truncate">{node.label}</span>
        </div>
        <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={onClose}>
          <X className="h-3 w-3" />
        </Button>
      </div>

      <ScrollArea className="flex-1 p-4 space-y-4">
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="space-y-1">
            <span className="text-muted-foreground">Type</span>
            <Badge variant="outline" className="text-[10px]">{config.label}</Badge>
          </div>
          <div className="space-y-1">
            <span className="text-muted-foreground">ID</span>
            <p className="text-[10px] font-mono truncate">{node.id}</p>
          </div>
        </div>

        {/* Evidence Provenance */}
        {typeof meta.evidence_id === "string" && meta.evidence_id && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Source Evidence</span>
            <p className="text-[10px] font-mono break-all bg-muted p-2 rounded">{metaStr("evidence_id")}</p>
          </div>
        )}

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

        {typeof meta.source === "string" && meta.source && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Extraction Source</span>
            <Badge variant="secondary" className="text-[10px]">{metaStr("source")}</Badge>
          </div>
        )}

        {typeof meta.detected_at === "string" && meta.detected_at && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">First Detected</span>
            <p className="text-[10px]">{new Date(metaStr("detected_at")).toLocaleString()}</p>
          </div>
        )}

        {typeof meta.normalized_value === "string" && meta.normalized_value && meta.normalized_value !== node.label && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Normalized Value</span>
            <p className="text-[10px]">{metaStr("normalized_value")}</p>
          </div>
        )}

        {metaBool("is_new") && (
          <Badge className="text-[10px] bg-green-500/10 text-green-700 border-green-200">New</Badge>
        )}

        {connectedEdges.length > 0 && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground flex items-center gap-1">
              <GitBranch className="h-3 w-3" /> Relationships ({connectedEdges.length})
            </span>
            <div className="space-y-1">
              {connectedEdges.map((edge) => {
                const otherNodeId = edge.source === node.id ? edge.target : edge.source;
                const otherNode = allNodes.find((n) => n.id === otherNodeId);
                const direction = edge.source === node.id ? "outgoing" : "incoming";
                return (
                  <div key={edge.id} className="p-2 rounded bg-muted/50 text-[10px] space-y-0.5">
                    <div className="flex items-center gap-1">
                      <Badge variant="outline" className="text-[9px]">{edge.type ?? "related"}</Badge>
                      <span className="text-muted-foreground">{direction}</span>
                    </div>
                    <p className="font-medium">{otherNode?.label ?? otherNodeId}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {connectedNodes.length > 0 && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Connected Entities ({connectedNodes.length})</span>
            <div className="flex flex-wrap gap-1">
              {connectedNodes.slice(0, 10).map((n) => {
                const nType = (n.type ?? "entity").toLowerCase();
                const nConfig = TYPE_CONFIG[nType] ?? TYPE_CONFIG.entity;
                const NIcon = nConfig.icon;
                return (
                  <Badge key={n.id} variant="secondary" className="text-[10px] gap-1">
                    <NIcon className={`h-3 w-3 ${nConfig.color}`} />
                    {n.label}
                  </Badge>
                );
              })}
            </div>
          </div>
        )}

        {Object.keys(meta).length > 0 && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Properties</span>
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
