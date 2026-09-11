import type { ID, ISOString, Nullable } from "./common";

export type ProcessingStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "cancelled"
  | string;

export interface QueueStats {
  queued: number;
  running: number;
  completed: number;
  failed: number;
  cancelled: number;
  active_workers: number;
  max_workers: number;
}

export interface ProcessingJob {
  id: ID;
  evidence_id: Nullable<string>;
  processors: string[];
  status: ProcessingStatus;
  queued_at?: Nullable<ISOString>;
  started_at?: Nullable<ISOString>;
  finished_at?: Nullable<ISOString>;
  result?: unknown;
  error?: unknown;
}

export interface JobProgress {
  job_id: ID;
  status: ProcessingStatus;
  progress: string;
  queued_at?: Nullable<ISOString>;
  started_at?: Nullable<ISOString>;
  finished_at?: Nullable<ISOString>;
  processors: string[];
  completed_processors: string[];
  error?: unknown;
}

export interface EnqueueRequest {
  processors?: string[];
}

export interface EnqueueResponse {
  job_id: ID;
}

export interface ForensicProcessRequest {
  enabled_processors?: string[];
  ocr_language?: string;
  run_ocr?: boolean;
  generate_thumbnails?: boolean;
}

export interface ForensicProcessResponse {
  evidence_id: ID;
  success: boolean;
  processors_run: string[];
  duration_seconds: number;
  errors: unknown;
  tags: string[];
}

// ── Distributed Processing Types ───────────────────────────────────────

export type DistributedTaskStatus =
  | "PENDING"
  | "QUEUED"
  | "CLAIMED"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED"
  | "RETRYING"
  | "DEAD_LETTERED"
  | string;

export type DistributedJobStatus =
  | "PENDING"
  | "QUEUED"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED"
  | "PAUSED"
  | string;

export type WorkerStatusType =
  | "idle"
  | "busy"
  | "offline"
  | "restarting"
  | string;

export interface DistributedTask {
  id: string;
  job_id?: string;
  processor_type: string;
  priority?: number;
  status: DistributedTaskStatus;
  payload?: Record<string, unknown>;
  dependencies?: string[];
  created_at?: string;
  started_at?: string;
  completed_at?: string;
  retry_count?: number;
  max_retries?: number;
  error?: string;
  worker_id?: string;
  progress?: number;
}

export interface DistributedJob {
  id: string;
  status: DistributedJobStatus;
  tasks?: DistributedTask[];
  task_count?: number;
  completed_count?: number;
  failed_count?: number;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
}

export interface WorkerInfo {
  worker_id: string;
  name?: string;
  status: WorkerStatusType;
  started_at?: string;
  last_heartbeat?: string;
  tasks_completed?: number;
  tasks_failed?: number;
  current_task_id?: string;
  capabilities?: string[];
  max_concurrency?: number;
  cpu_usage?: number;
  memory_usage?: number;
}

export interface QueueDepth {
  critical?: number;
  high?: number;
  normal?: number;
  low?: number;
  total?: number;
}

export interface DistributedMetrics {
  tasks_submitted?: number;
  tasks_completed?: number;
  tasks_failed?: number;
  tasks_retried?: number;
  tasks_dead_lettered?: number;
  queue_depth?: number;
  active_workers?: number;
  total_workers?: number;
  uptime_seconds?: number;
  [key: string]: unknown;
}

export interface DLQItem {
  task_id: string;
  processor_type?: string;
  error?: string;
  created_at?: string;
  retry_count?: number;
}

export interface TaskActionResponse {
  detail: string;
  task_id: string;
}

export interface JobActionResponse {
  detail: string;
  job_id: string;
}

export interface TaskProgressResponse {
  task_id: string;
  status: DistributedTaskStatus;
  progress?: number;
  worker_id?: string;
  error?: string;
  started_at?: string;
  completed_at?: string;
}
