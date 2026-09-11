import type { Dict, ID, Nullable } from "./common";

/** TimelineEvent as returned by GET /timeline. */
export interface TimelineEvent {
  id: ID;
  evidence_id?: Nullable<ID>;
  case_id?: Nullable<ID>;
  timestamp: string;
  title: string;
  description: string;
  source: string;
  metadata?: Nullable<Dict>;
}

export interface TimelineQuery {
  case_id?: string;
  limit?: number;
}
