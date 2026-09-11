import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import type {
  TSKCapabilities,
  TSKEnqueueRequest,
  TSKJobStatus,
  TSKPipelineResult,
  TSKProcessRequest,
} from "@/types/tsk";

export const tskService = {
  capabilities: (): Promise<TSKCapabilities> =>
    api.get<TSKCapabilities>(API.tsk.capabilities),

  process: (request: TSKProcessRequest): Promise<TSKPipelineResult> =>
    api.post<TSKPipelineResult>(API.tsk.process, request),

  enqueue: (request: TSKEnqueueRequest): Promise<{ job_id: string; status: string }> =>
    api.post<{ job_id: string; status: string }>(API.tsk.enqueue, request),

  status: (jobId: string): Promise<TSKJobStatus> =>
    api.get<TSKJobStatus>(API.tsk.status(jobId)),
};
