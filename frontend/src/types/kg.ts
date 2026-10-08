import type { Dict, ID, Nullable } from "./common";

export type FactClassification = "OBSERVED" | "DERIVED" | "CANDIDATE" | "HYPOTHESIS" | "REVIEWED";

/** A node in the case knowledge graph. */
export interface GraphNode {
  id: ID;
  label: string;
  type?: string;
  color?: string;
  val?: number;
  confidence?: number;
  fact_classification?: FactClassification;
  properties?: Dict;
  provenance?: Dict;
  // 3D Spatial coordinates
  x?: number;
  y?: number;
  z?: number;
  fx?: number;
  fy?: number;
  fz?: number;
  // GDS metrics
  pagerank?: number;
  centralityScore?: number;
  degree?: number;
  communityId?: number;
}

/** A directed edge in the case knowledge graph. */
export interface GraphEdge {
  id: ID;
  source: ID;
  target: ID;
  type?: string;
  label?: string;
  confidence?: number;
  fact_classification?: FactClassification;
  evidence_id?: string;
  artifact_id?: string;
  source_text?: string;
  processor?: string;
  properties?: Dict;
}

export interface CaseGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  depth?: number;
  total_nodes?: number;
  total_edges?: number;
}

export interface CypherQuery {
  cypher: string;
  params?: Nullable<Dict>;
}

export interface KGQueryResponse {
  results: unknown[];
}

export interface EntityRef {
  name: string;
  type?: string;
}

export interface KGEntitiesResponse {
  entities: EntityRef[];
}

export interface KGIngestResponse {
  ingested_entities: number;
  relationships: number;
  timeline: number;
}
