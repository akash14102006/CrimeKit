import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import { refresh as descopeRefresh } from "@descope/react-sdk";
import { useAuthStore } from "@/store/authStore";
import { toast } from "@/components/ui/toast";
import { env } from "@/config/env";

interface RetriableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const getBaseUrl = () => env.apiBaseUrl;

export const apiClient: AxiosInstance = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
  timeout: env.requestTimeoutMs,
});

/**
 * Request interceptor — attach Descope session JWT to every outgoing request.
 */
apiClient.interceptors.request.use((config) => {
  config.baseURL = getBaseUrl();
  // Read token from Zustand store (safely handles SSR/hydration)
  try {
    const state = useAuthStore.getState();
    if (state && state.sessionToken) {
      config.headers.Authorization = `Bearer ${state.sessionToken}`;
    }
  } catch {
    // Zustand store not yet initialized during hydration
  }
  return config;
});

let isRefreshing = false;
let refreshSubscribers: Array<(token: string | null) => void> = [];
let redirectThrottleTimer: ReturnType<typeof setTimeout> | null = null;

const flushRefreshSubscribers = (token: string | null) => {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
};

function isDescopeToken(token: string): boolean {
  if (!token || typeof token !== "string") return false;
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return false;
    const header = JSON.parse(atob(parts[0]));
    return header.alg && header.alg !== "HS256";
  } catch {
    return false;
  }
}

function handleAuthFailure(error: AxiosError) {
  const { clearSession } = useAuthStore.getState();
  clearSession();
  isRefreshing = false;
  flushRefreshSubscribers(null);

  if (typeof window !== "undefined") {
    const pathname = window.location.pathname;
    if (!pathname.startsWith("/login") && !pathname.startsWith("/mfa") && !pathname.startsWith("/session-expired")) {
      if (!redirectThrottleTimer) {
        redirectThrottleTimer = setTimeout(() => {
          redirectThrottleTimer = null;
          window.location.href = "/login";
        }, 100);
      }
    }
  }
}

const isAuthEndpoint = (url?: string) =>
  typeof url === "string" && (url.includes("/auth/login") || url.includes("/auth/refresh"));

let lastNetworkToastTime = 0;
function throttleNetworkToast() {
  const now = Date.now();
  if (now - lastNetworkToastTime > 6000) {
    lastNetworkToastTime = now;
    toast.add({
      title: "Network Error",
      description:
        "Could not connect to the server. Please check that the backend is running.",
      type: "error",
    });
  }
}

/**
 * Response interceptor — handle 401 with concurrency-safe session refresh.
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableConfig | undefined;

    if (error.response?.status === 401) {
      const url = originalRequest?.url || "";

      // 1. Never retry auth endpoints or requests already retried
      if (!originalRequest || originalRequest._retry || isAuthEndpoint(url)) {
        handleAuthFailure(error);
        return Promise.reject(error);
      }

      // 2. If a refresh is already in flight, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshSubscribers.push((token) => {
            if (!token) return reject(error);
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            originalRequest._retry = true;
            resolve(apiClient(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { refreshToken, sessionToken } = useAuthStore.getState();

        if (!refreshToken) {
          handleAuthFailure(error);
          return Promise.reject(error);
        }

        let newSession: string | null = null;
        let newRefresh: string | null = null;

        if (isDescopeToken(refreshToken) || (sessionToken && isDescopeToken(sessionToken))) {
          // Attempt Descope session refresh using the SDK
          try {
            const refreshResult = await descopeRefresh(refreshToken);
            if (refreshResult?.data?.sessionJwt) {
              newSession = refreshResult.data.sessionJwt;
              newRefresh = refreshResult.data.refreshJwt ?? refreshToken;
            }
          } catch (dsErr) {
            console.warn("[CrimeKit] Descope refresh failed:", dsErr);
          }
        } else {
          // Attempt Backend refresh for local JWT tokens
          try {
            const resp = await axios.post<{ access_token: string; refresh_token?: string }>(
              `${getBaseUrl()}/auth/refresh`,
              { refresh_token: refreshToken },
              { timeout: 5000 },
            );
            if (resp.data?.access_token) {
              newSession = resp.data.access_token;
              newRefresh = resp.data.refresh_token ?? refreshToken;
            }
          } catch (beErr) {
            console.warn("[CrimeKit] Backend token refresh failed:", beErr);
          }
        }

        if (newSession) {
          useAuthStore.getState().setSession(newSession, newRefresh);
          isRefreshing = false;
          flushRefreshSubscribers(newSession);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newSession}`;
          }
          return apiClient(originalRequest);
        }

        // Refresh failed — clear session and reject
        handleAuthFailure(error);
        return Promise.reject(error);
      } catch (refreshError) {
        handleAuthFailure(error);
        return Promise.reject(refreshError);
      }
    }

    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as Record<string, unknown> | undefined;
      const message = (data?.message as string) || (data?.detail as string);
      if (status === 401) {
        toast.add({
          title: "Session Expired",
          description: "Please log in again.",
          type: "error",
        });
      } else if (status === 403) {
        toast.add({
          title: "Access Denied",
          description: message || "You don't have permission to perform this action.",
          type: "error",
        });
      } else if (status === 404) {
        toast.add({
          title: "Not Found",
          description: message || "The requested resource was not found.",
          type: "error",
        });
      } else if (status === 422) {
        toast.add({
          title: "Validation Error",
          description: message || "Please check your input and try again.",
          type: "error",
        });
      } else if (status >= 500) {
        toast.add({
          title: "Server Error",
          description: message || "An unexpected error occurred on the server.",
          type: "error",
        });
      }
    } else if (error.request) {
      // Distinguish between actual network failures and request timeouts / aborts / canceled requests.
      const isTimeout = error.code === "ECONNABORTED" || error.message?.includes("timeout");
      const isParseError =
        error.code === "ERR_BAD_RESPONSE" ||
        error.code === "ERR_PARSE_RESPONSE";
      const isAbort =
        axios.isCancel(error) ||
        error.code === "ERR_CANCELED" ||
        error.name === "CanceledError" ||
        error.name === "AbortError" ||
        Boolean(originalRequest?.signal?.aborted);

      const isWindowNavigating =
        typeof window !== "undefined" &&
        (!window.navigator.onLine || window.location.pathname === "/login");

      if (!isParseError && !isTimeout && !isAbort && !isWindowNavigating) {
        throttleNetworkToast();
      }
    }

    return Promise.reject(error);
  },
);

/** Extract a human-readable message from an unknown error. */
export function getErrorMessage(error: unknown, fallback = "Something went wrong."): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as Record<string, unknown> | undefined;
    if (data) {
      // Backend format: {"error":"...", "message":"...", "detail":"..."}
      if (typeof data.message === "string") return data.message;
      if (typeof data.detail === "string") return data.detail;
      // FastAPI validation errors: {"detail": [{"msg":"...", ...}]}
      if (Array.isArray(data.detail) && data.detail.length > 0) {
        const first = data.detail[0] as Record<string, unknown>;
        if (typeof first.msg === "string") return first.msg;
      }
    }
  }
  if (error instanceof Error) return error.message;
  return fallback;
}

async function withBody<T>(
  method: "post" | "put" | "patch",
  url: string,
  data?: unknown,
  config?: InternalAxiosRequestConfig,
): Promise<T> {
  const response = await apiClient.request<T>({
    method,
    url,
    data,
    ...config,
  });
  return response.data;
}

export const api = {
  get: async <T>(
    url: string,
    config?: import("axios").AxiosRequestConfig,
  ): Promise<T> => {
    const response = await apiClient.get<T>(url, config);
    return response.data;
  },
  post: <T>(url: string, data?: unknown, config?: import("axios").AxiosRequestConfig) =>
    withBody<T>("post", url, data, config as InternalAxiosRequestConfig),
  put: <T>(url: string, data?: unknown, config?: import("axios").AxiosRequestConfig) =>
    withBody<T>("put", url, data, config as InternalAxiosRequestConfig),
  patch: <T>(url: string, data?: unknown, config?: import("axios").AxiosRequestConfig) =>
    withBody<T>("patch", url, data, config as InternalAxiosRequestConfig),
  delete: async <T>(
    url: string,
    config?: import("axios").AxiosRequestConfig,
  ): Promise<T> => {
    const response = await apiClient.delete<T>(url, {
      ...config,
      // Ensure axios doesn't try to JSON.parse an empty 204 body.
      responseType: (config?.responseType as "text") ?? "text",
    });
    // 204 No Content — response.data is empty string; coerce to void-like return.
    if (response.status === 204 || !response.data) {
      return undefined as T;
    }
    return response.data;
  },
  upload: async <T>(
    url: string,
    file: File | Blob,
    extraFields?: Record<string, string>,
    config?: {
      onUploadProgress?: (percentCompleted: number) => void;
    },
  ): Promise<T> => {
    const form = new FormData();
    form.append("file", file);
    if (extraFields) {
      Object.entries(extraFields).forEach(([key, value]) =>
        form.append(key, value),
      );
    }
    const { onUploadProgress } = config ?? {};
    const response = await apiClient.post<T>(url, form, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 600_000,
      onUploadProgress: (progressEvent) => {
        if (onUploadProgress && progressEvent.total) {
          onUploadProgress(
            Math.round((progressEvent.loaded * 100) / progressEvent.total),
          );
        }
      },
    });
    return response.data;
  },
};

export default apiClient;
