import { ApiErrorBody } from "@/types/api";

/** Structured error surfaced to UI code. */
export class AppError extends Error {
  readonly status?: number;
  readonly code?: string;
  readonly detail?: unknown;
  readonly retryable: boolean;

  constructor(message: string, options?: {
    status?: number;
    code?: string;
    detail?: unknown;
    retryable?: boolean;
    cause?: unknown;
  }) {
    super(message, { cause: options?.cause });
    this.name = "AppError";
    this.status = options?.status;
    this.code = options?.code;
    this.detail = options?.detail;
    this.retryable = options?.retryable ?? false;
  }

  static fromHttpStatus(status: number, body?: unknown, message?: string) {
    const detail = (body as ApiErrorBody | undefined)?.detail;
    let msg = message;
    if (!msg) {
      if (typeof detail === "string") msg = detail;
      else if (detail && typeof detail === "object") {
        msg = (detail as { message?: string }).message ?? "Request failed.";
      } else msg = "Request failed.";
    }
    return new AppError(msg, {
      status,
      detail: body,
      retryable: status >= 500,
    });
  }
}

export function isAppError(error: unknown): error is AppError {
  return error instanceof AppError;
}
