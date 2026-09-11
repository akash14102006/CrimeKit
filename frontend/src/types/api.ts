import type { ApiErrorBody } from "./common";

export interface ApiRequestOptions {
  signal?: AbortSignal;
  headers?: Record<string, string>;
  /** When true, the axios interceptor refreshes the access token on 401. */
  withAuth?: boolean;
}

export interface ApiErrorMeta {
  status?: number;
  detail?: unknown;
  retryable?: boolean;
}

export type { ApiErrorBody };
