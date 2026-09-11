import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { kgService } from "@/services/kgService";
import type { CypherQuery } from "@/types/kg";

export function useCaseKnowledgeGraph(caseId?: string, depth = 2) {
  return useQuery({
    queryKey: ["kg", "case", caseId, depth],
    queryFn: () => kgService.caseGraph(caseId as string, depth),
    enabled: !!caseId,
  });
}

export function useEntityNeighbors(
  entityType?: string,
  entityName?: string,
  depth = 1,
) {
  return useQuery({
    queryKey: ["kg", "entity-neighbors", entityType, entityName, depth],
    queryFn: () =>
      kgService.entityNeighbors(entityType as string, entityName as string, depth),
    enabled: !!entityType && !!entityName,
  });
}

export function useCaseGraphSync(caseId?: string, since?: number) {
  return useQuery({
    queryKey: ["kg", "sync", caseId, since],
    queryFn: () => kgService.caseSync(caseId as string, since),
    enabled: !!caseId,
    refetchInterval: 30000,
  });
}

export function useKnowledgeGraphEntities(name?: string) {
  return useQuery({
    queryKey: ["kg", "entities", name ?? ""],
    queryFn: () => kgService.entities(name),
  });
}

export function useKnowledgeGraphQuery() {
  return useMutation({
    mutationFn: (payload: CypherQuery) => kgService.query(payload),
  });
}

export function useIngestEvidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (evidenceId: string) => kgService.ingestEvidence(evidenceId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["kg"] }),
  });
}
