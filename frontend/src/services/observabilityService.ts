import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import type { MetricsResponse } from "@/types/dashboard";

export const observabilityService = {
  metricsJson: (): Promise<MetricsResponse> =>
    api.get<MetricsResponse>(API.observability.metricsJson),
};
