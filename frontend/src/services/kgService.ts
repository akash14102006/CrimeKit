import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import {
  CypherQuery,
  EntityRef,
  KGEntitiesResponse,
  KGIngestResponse,
  KGQueryResponse,
} from "@/types/kg";

export const kgService = {
  query: (payload: CypherQuery): Promise<KGQueryResponse> =>
    api.post<KGQueryResponse>(API.kg.query, payload),

  entities: (name?: string): Promise<KGEntitiesResponse> =>
    api.get<KGEntitiesResponse>(
      name ? `${API.kg.entities}?name=${encodeURIComponent(name)}` : API.kg.entities,
    ),

  caseGraph: (caseId: string, depth = 2): Promise<{ graph: unknown[]; depth: number }> =>
    api.get<{ graph: unknown[]; depth: number }>(
      `${API.kg.caseGraph(caseId)}?depth=${depth}`,
    ),

  entityNeighbors: (
    entityType: string,
    entityName: string,
    depth = 1,
  ): Promise<{ nodes: unknown[]; depth: number }> =>
    api.get<{ nodes: unknown[]; depth: number }>(
      `${API.kg.entityNeighbors(entityType, entityName)}?depth=${depth}`,
    ),

  caseSync: (
    caseId: string,
    since?: number,
  ): Promise<{ version: number; events: unknown[]; nodes?: unknown[]; has_more: boolean }> =>
    api.get<{ version: number; events: unknown[]; nodes?: unknown[]; has_more: boolean }>(
      `${API.kg.caseSync(caseId)}${since ? `?since=${since}` : ""}`,
    ),

  ingestEvidence: (evidenceId: string): Promise<KGIngestResponse> =>
    api.post<KGIngestResponse>(API.kg.ingestEvidence(evidenceId)),
};

export type { EntityRef };
