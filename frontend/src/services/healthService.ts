import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import {
  DetailedHealthResponse,
  HealthStatus,
  LivenessResponse,
  ReadinessResponse,
} from "@/types/health";

export const healthService = {
  root: (): Promise<HealthStatus> => api.get<HealthStatus>(API.health.root),

  ready: (): Promise<ReadinessResponse> =>
    api.get<ReadinessResponse>(API.health.ready),

  live: (): Promise<LivenessResponse> =>
    api.get<LivenessResponse>(API.health.live),

  detailed: (): Promise<DetailedHealthResponse> =>
    api.get<DetailedHealthResponse>(API.health.detailed),
};
