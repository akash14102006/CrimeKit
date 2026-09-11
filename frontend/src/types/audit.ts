import type { Dict, ID, ISOString, Nullable } from "./common";

/**
 * Audit events are written server-side by the backend and read through the
 * compliance audit endpoints (there is no standalone audit router).
 */
export interface AuditLogEntry {
  id: ID;
  action: string;
  entity_type?: Nullable<string>;
  entity_id?: Nullable<ID>;
  actor_id?: Nullable<string>;
  actor_email?: Nullable<string>;
  details?: Dict;
  created_at?: ISOString;
}
