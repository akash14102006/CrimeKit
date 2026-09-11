import type { ISOString } from "./common";

export interface HealthStatus {
  status: string;
  service?: string;
  timestamp?: ISOString;
}

export interface ReadinessCheck {
  status: string;
  service: string;
  latency_ms: number;
  message?: string;
}

export interface ReadinessResponse {
  status: "ready" | "not_ready";
  timestamp: ISOString;
  checks: ReadinessCheck[];
}

export interface LivenessResponse {
  status: "alive";
  service: string;
  timestamp: ISOString;
  uptime_seconds: number;
}

export interface DetailedCheck extends ReadinessCheck {
  tables?: Record<string, number>;
}

export interface DetailedHealthResponse {
  status: "healthy" | "degraded";
  service: string;
  timestamp: ISOString;
  version?: string;
  environment?: string;
  checks: DetailedCheck[];
}
