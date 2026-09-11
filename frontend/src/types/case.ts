import type { ID, ISOString, Nullable } from "./common";

export type CaseStatus = "open" | "review" | "closed" | string;
export type CasePriority = "low" | "medium" | "high" | "critical";

export interface CaseCreate {
  title: string;
  description?: Nullable<string>;
  priority?: CasePriority;
}

export interface CaseUpdate {
  title?: string;
  description?: Nullable<string>;
  status?: CaseStatus;
  priority?: CasePriority;
  assigned_to?: Nullable<string>;
}

/** CaseOut as returned by the backend (ORM-backed). */
export interface CaseOut {
  id: ID;
  title: string;
  description: Nullable<string>;
  status: Nullable<string>;
  priority: Nullable<string>;
  assigned_to: Nullable<ID>;
  created_by: Nullable<ID>;
  created_at?: ISOString;
  updated_at?: ISOString;
}

export interface CaseListResponse {
  items: CaseOut[];
  total: number;
  limit: number;
  offset: number;
  page: number;
}

export type CaseSummary = CaseOut;
