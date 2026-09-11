import type { Dict, ID, ISOString, Nullable } from "./common";

/** An uploaded evidence artifact (list + detail shapes). */
export interface Evidence {
  id: ID;
  case_id: Nullable<string>;
  filename: string;
  sha256: string;
  mime_type: Nullable<string>;
  size: number;
  uploaded_at?: Nullable<ISOString>;
  uploaded_by?: Nullable<ID>;
  metadata?: Nullable<Dict>;
}

export interface ForensicImageMetadata {
  evidence_type?: string;
  image_format?: string;
  processor?: string;
  capability?: "supported" | "unsupported";
  capability_reason?: string;
  forensic_image?: {
    reason?: string;
    capability?: "supported" | "unsupported";
  };
}

/** Paginated evidence list response. */
export interface EvidenceListResponse {
  items: Evidence[];
  total: number;
  page: number;
  limit: number;
  offset: number;
}

/** Response from POST /evidence/upload. */
export interface EvidenceUploadResponse {
  id: ID;
  sha256: string;
  size: number;
  mime_type: string;
}

export type UploadSessionStatus =
  | "queued"
  | "starting"
  | "in_progress"
  | "paused"
  | "completed"
  | "failed"
  | "cancelled"
  | "needs_file";

export interface UploadStartRequest {
  filename: string;
  file_size: number;
  chunk_size: number;
  case_id?: string;
  mime_type?: string;
  sha256?: string;
}

export interface UploadStartResponse {
  upload_id: ID;
  session_id: ID;
  chunk_size: number;
  total_chunks: number;
  bucket: string;
  object_key: string;
  status: string;
}

export interface UploadChunkResult {
  session_id: ID;
  chunk_number: number;
  etag: string;
  status: string;
  completed_chunks: number;
  total_chunks: number;
}

export interface MultipartPart {
  PartNumber: number;
  ETag: string;
}

export interface UploadCompleteResponse {
  session_id: ID;
  evidence_id: ID;
  sha256: string;
  md5?: string | null;
  size: number;
  status: string;
}

export interface UploadChunkStatus {
  chunk_number: number;
  size: number;
  status: string;
  retries: number;
  etag?: string | null;
  error_message?: string | null;
}

export interface UploadSessionStatusResponse {
  id: ID;
  filename: string;
  file_size: number;
  chunk_size: number;
  total_chunks: number;
  completed_chunks: number;
  status: string;
  sha256?: string | null;
  md5?: string | null;
  evidence_id?: string | null;
  error_message?: string | null;
  created_at?: ISOString | null;
  updated_at?: ISOString | null;
  completed_at?: ISOString | null;
  bucket: string;
  object_key: string;
  upload_id: string;
  completed_part_numbers: number[];
  parts: MultipartPart[];
  chunks: UploadChunkStatus[];
}

/** A custody-chain entry returned by GET /evidence/{id}/custody. */
export interface CustodyHistoryEntry {
  id: ID;
  action: string;
  actor_id?: Nullable<string>;
  timestamp?: Nullable<string>;
  details?: Dict;
}

export interface CustodyStatus {
  evidence_id: ID;
  integrity_ok: boolean;
  history: CustodyHistoryEntry[];
}

export interface CustodyAppendRequest {
  previous_owner?: string;
  new_owner?: string;
  location?: string;
  notes?: string;
  signature?: string;
  action?: string;
}

export interface CustodyAppendResponse {
  custody_id: string;
  integrity_ok: boolean;
}

/** Forensic processing result for an evidence item. */
export interface ForensicResult {
  id: string;
  evidence_id: string;
  processor: string;
  result: Dict;
  created_at?: ISOString;
}
