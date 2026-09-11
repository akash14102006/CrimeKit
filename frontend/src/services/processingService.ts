import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import {
  EnqueueRequest,
  EnqueueResponse,
  ForensicProcessRequest,
  ForensicProcessResponse,
  JobProgress,
  ProcessingJob,
  QueueStats,
  DistributedTask,
  DistributedJob,
  DistributedJobStatus,
  DistributedTaskStatus,
  WorkerInfo,
  QueueDepth,
  DistributedMetrics,
  DLQItem,
  TaskActionResponse,
  JobActionResponse,
  TaskProgressResponse,
} from "@/types/processing";

export const processingService = {
  enqueue: (
    evidenceId: string,
    payload?: EnqueueRequest,
  ): Promise<EnqueueResponse> =>
    api.post<EnqueueResponse>(
      API.processing.enqueue(evidenceId),
      payload ?? {},
    ),

  job: (jobId: string): Promise<ProcessingJob> =>
    api.get<ProcessingJob>(API.processing.job(jobId)),

  cancelJob: (jobId: string): Promise<{ detail: string; job_id: string }> =>
    api.post<{ detail: string; job_id: string }>(
      API.processing.cancelJob(jobId),
    ),

  jobProgress: (jobId: string): Promise<JobProgress> =>
    api.get<JobProgress>(API.processing.jobProgress(jobId)),

  queueStats: (): Promise<QueueStats> =>
    api.get<QueueStats>(API.processing.queueStats),

  forensicProcess: (
    evidenceId: string,
    payload?: ForensicProcessRequest,
  ): Promise<ForensicProcessResponse> =>
    api.post<ForensicProcessResponse>(
      API.processing.forensic(evidenceId),
      payload ?? {},
    ),

  processors: (): Promise<{ processors: string[] }> =>
    api.get<{ processors: string[] }>(API.processing.processors),
};

export interface DistributedEnqueueTask {
  processor_type: string;
  payload?: Record<string, unknown>;
  priority?: number;
  dependencies?: string[];
}

export const distributedService = {
  enqueueTask: (
    task: DistributedEnqueueTask,
  ): Promise<TaskActionResponse> =>
    api.post<TaskActionResponse>(API.distributed.enqueueTask, task),

  enqueueBatch: (
    tasks: DistributedEnqueueTask[],
  ): Promise<{ detail: string; task_ids: string[]; count: number }> =>
    api.post<{ detail: string; task_ids: string[]; count: number }>(
      API.distributed.enqueueBatch,
      { tasks },
    ),

  taskProgress: (taskId: string): Promise<TaskProgressResponse> =>
    api.get<TaskProgressResponse>(API.distributed.taskProgress(taskId)),

  cancelTask: (taskId: string): Promise<TaskActionResponse> =>
    api.post<TaskActionResponse>(API.distributed.cancelTask(taskId)),

  retryTask: (taskId: string): Promise<TaskActionResponse> =>
    api.post<TaskActionResponse>(API.distributed.retryTask(taskId)),

  job: (jobId: string): Promise<DistributedJob> =>
    api.get<DistributedJob>(API.distributed.job(jobId)),

  cancelJob: (jobId: string): Promise<JobActionResponse> =>
    api.post<JobActionResponse>(API.distributed.cancelJob(jobId)),

  resumeJob: (jobId: string): Promise<JobActionResponse> =>
    api.post<JobActionResponse>(API.distributed.resumeJob(jobId)),

  queueDepth: (): Promise<QueueDepth> =>
    api.get<QueueDepth>(API.distributed.queueDepth),

  workers: (): Promise<{ workers: WorkerInfo[]; total: number }> =>
    api.get<{ workers: WorkerInfo[]; total: number }>(
      API.distributed.workers,
    ),

  worker: (workerId: string): Promise<WorkerInfo> =>
    api.get<WorkerInfo>(API.distributed.worker(workerId)),

  metrics: (): Promise<DistributedMetrics> =>
    api.get<DistributedMetrics>(API.distributed.metrics),

  dlq: (): Promise<{ items: DLQItem[]; total: number }> =>
    api.get<{ items: DLQItem[]; total: number }>(API.distributed.dlq),

  dlqReplay: (taskId: string): Promise<TaskActionResponse> =>
    api.post<TaskActionResponse>(API.distributed.dlqReplay(taskId)),

  dlqPurge: (): Promise<{ detail: string; purged_count: number }> =>
    api.delete<{ detail: string; purged_count: number }>(
      API.distributed.dlqPurge,
    ),
};
