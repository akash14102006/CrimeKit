import type { Dict, ID, ISOString, Nullable } from "./common";

export type SearchMode = "hybrid" | "semantic" | "keyword" | "vector" | string;

export interface SearchHighlight {
  field: string;
  snippet: string;
  offsets?: unknown;
}

export interface SearchResult {
  id: ID;
  type: string;
  score: number;
  title: string;
  snippet: string;
  highlights?: SearchHighlight[];
  metadata: Dict;
  created_at?: Nullable<ISOString>;
  updated_at?: Nullable<ISOString>;
}

export interface SearchFacetBucket {
  value: string;
  count: number;
}

export interface SearchFacet {
  name: string;
  type?: string;
  buckets: SearchFacetBucket[];
  total?: number;
}

export interface SearchResponse {
  query: string;
  total: number;
  took_ms: number;
  tier: string;
  mode: SearchMode;
  page: number;
  page_size: number;
  max_score: number;
  results: SearchResult[];
  facets: SearchFacet[];
}

export interface GeneralSearchRequest {
  query: string;
  mode?: SearchMode;
  filters?: Nullable<Dict>;
  page?: number;
  page_size?: number;
}

export interface EvidenceSearchRequest {
  sha256?: string;
  filename?: string;
  mime_type?: string;
  page?: number;
  page_size?: number;
}

export interface CaseSearchRequest {
  title?: string;
  status?: string;
  created_by?: string;
  page?: number;
  page_size?: number;
}

export interface TimelineSearchRequest {
  event_type?: Nullable<string>;
  entity_ids?: Nullable<Array<string>>;
  page?: number;
  page_size?: number;
}

export interface EntitySearchRequest {
  query: string;
  entity_type?: Nullable<string>;
  page?: number;
  page_size?: number;
}

export interface RelationshipSearchRequest {
  entity_id: string;
  max_depth?: number;
  relationship_types?: Nullable<string[]>;
}

export interface HybridSearchRequest {
  query: string;
  page?: number;
  page_size?: number;
}

export interface SemanticSearchRequest {
  query: string;
  page?: number;
  page_size?: number;
}

export interface CrossCorrelationRequest {
  query: string;
  page?: number;
  page_size?: number;
}

export interface ReindexResponse {
  cases: number;
  evidence: number;
  documents: number;
  forensic_results: number;
  audit_logs: number;
  embeddings: number;
}

export interface SearchHealthResponse {
  status: string;
  [key: string]: unknown;
}
