import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import {
  CaseSearchRequest,
  CrossCorrelationRequest,
  EntitySearchRequest,
  EvidenceSearchRequest,
  GeneralSearchRequest,
  HybridSearchRequest,
  ReindexResponse,
  SearchHealthResponse,
  SearchResponse,
  SemanticSearchRequest,
  TimelineSearchRequest,
} from "@/types/search";

export const searchService = {
  query: (payload: GeneralSearchRequest): Promise<SearchResponse> =>
    api.post<SearchResponse>(API.search.query, payload),

  searchEvidence: (
    payload: EvidenceSearchRequest,
  ): Promise<SearchResponse["results"]> =>
    api.post<SearchResponse["results"]>(API.search.evidence, payload),

  searchCases: (payload: CaseSearchRequest): Promise<SearchResponse["results"]> =>
    api.post<SearchResponse["results"]>(API.search.cases, payload),

  searchTimeline: (
    payload: TimelineSearchRequest,
  ): Promise<SearchResponse["results"]> =>
    api.post<SearchResponse["results"]>(API.search.timeline, payload),

  searchEntities: (
    payload: EntitySearchRequest,
  ): Promise<SearchResponse["results"]> =>
    api.post<SearchResponse["results"]>(API.search.entities, payload),

  hybrid: (payload: HybridSearchRequest): Promise<SearchResponse["results"]> =>
    api.post<SearchResponse["results"]>(API.search.hybrid, payload),

  semantic: (payload: SemanticSearchRequest): Promise<SearchResponse["results"]> =>
    api.post<SearchResponse["results"]>(API.search.semantic, payload),

  crossCorrelate: (
    payload: CrossCorrelationRequest,
  ): Promise<SearchResponse["results"]> =>
    api.post<SearchResponse["results"]>(API.search.crossCorrelate, payload),

  reindex: (): Promise<ReindexResponse> =>
    api.post<ReindexResponse>(API.search.reindex),

  health: (): Promise<SearchHealthResponse> =>
    api.get<SearchHealthResponse>(API.search.health),
};
