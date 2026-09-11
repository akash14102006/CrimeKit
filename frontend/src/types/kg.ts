import type { Dict, ID, Nullable } from "./common";

/** A node in the case knowledge graph. */
export interface GraphNode {
  id: ID;
  label: string;
  type?: string;
  properties?: Dict;
}

/** A directed edge in the case knowledge graph. */
export interface GraphEdge {
  id: ID;
  source: ID;
  target: ID;
  type?: string;
  label?: string;
  properties?: Dict;
}

export interface CaseGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
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
