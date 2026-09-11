"use client";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  GitBranch,
  RefreshCw,
  Users,
  MapPin,
  Smartphone,
  Building,
  FileSearch,
} from "lucide-react";
import { useCaseKnowledgeGraph } from "@/hooks/queries/useKnowledgeGraph";
import { useWorkspace } from "@/hooks/queries/useWorkspace";

interface Props {
  caseId: string;
}

const ENTITY_ICONS: Record<string, typeof Users> = {
  person: Users,
  location: MapPin,
  device: Smartphone,
  organization: Building,
  evidence: FileSearch,
};

export function KnowledgeGraphPanel({ caseId }: Props) {
  const { data: kgData, isLoading: kgLoading, error: kgError, refetch } = useCaseKnowledgeGraph(caseId);
  const { data: workspace } = useWorkspace(caseId);
  const kgSummary = workspace?.knowledge_graph;

  if (kgLoading) {
    return (
      <div className="space-y-3 p-3">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </div>
    );
  }

  if (kgError) {
    return (
      <div className="space-y-3 p-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-semibold flex items-center gap-1.5">
            <GitBranch className="h-3.5 w-3.5" />
            Knowledge Graph
          </h4>
          <Button variant="ghost" size="sm" className="h-6 px-2" onClick={() => refetch()}>
            <RefreshCw className="h-3 w-3" />
          </Button>
        </div>
        <div className="text-center py-4">
          <GitBranch className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
          <p className="text-xs text-muted-foreground">Knowledge graph unavailable</p>
          <p className="text-[10px] text-muted-foreground mt-1">Neo4j database may not be configured. Contact an administrator.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 p-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold flex items-center gap-1.5">
          <GitBranch className="h-3.5 w-3.5" />
          Knowledge Graph
        </h4>
        <Button variant="ghost" size="sm" className="h-6 px-2" onClick={() => refetch()}>
          <RefreshCw className="h-3 w-3" />
        </Button>
      </div>

      {kgSummary && !kgSummary.available ? (
        <div className="text-center py-4">
          <GitBranch className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
          <p className="text-xs text-muted-foreground">Knowledge graph not built yet</p>
          <p className="text-[10px] text-muted-foreground mt-1">Ingest evidence into the KG to discover relationships</p>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2 text-center text-[10px]">
            <div className="p-2 rounded bg-muted/50">
              <p className="font-medium text-foreground">{kgSummary?.entity_count ?? 0}</p>
              <p className="text-muted-foreground">Entities</p>
            </div>
            <div className="p-2 rounded bg-muted/50">
              <p className="font-medium text-foreground">{kgSummary?.relationship_count ?? 0}</p>
              <p className="text-muted-foreground">Relationships</p>
            </div>
          </div>

          {kgData?.graph && Array.isArray(kgData.graph) && kgData.graph.length > 0 && (
            <div className="space-y-1">
              <span className="text-[10px] font-medium text-muted-foreground uppercase">Entities</span>
              {(kgData.graph as Record<string, unknown>[]).slice(0, 20).map((node: Record<string, unknown>, i: number) => {
                const Icon = ENTITY_ICONS[(node.type as string)?.toLowerCase()] ?? Users;
                return (
                  <div key={i} className="flex items-center gap-2 text-xs py-1">
                    <Icon className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <span className="truncate">{(node.label as string) ?? (node.name as string) ?? `Entity ${i + 1}`}</span>
                    {typeof node.type === "string" && (
                      <Badge variant="outline" className="text-[10px] ml-auto">
                        {node.type}
                      </Badge>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {kgSummary?.notes && kgSummary.notes.length > 0 && (
            <div className="space-y-1">
              <span className="text-[10px] font-medium text-muted-foreground uppercase">Notes</span>
              {kgSummary.notes.map((note, i) => (
                <p key={i} className="text-[10px] text-muted-foreground italic">{note}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
