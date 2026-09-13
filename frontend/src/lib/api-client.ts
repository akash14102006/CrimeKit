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

const flushRefreshSubscribers = (token: string | null) => {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
};

const isAuthEndpoint = (url?: string) =>
  typeof url === "string" && url.includes("/auth/");

/**
 * Response interceptor — handle 401 with Descope session refresh.
 *
 * Strategy:
 * 1. On 401, check if we have a Descope refresh token.
 * 2. If yes, attempt to refresh the session via Descope's refresh endpoint.
 * 3. If refresh succeeds, retry the original request with the new token.
 * 4. If refresh fails, clear session and redirect to login.
 *
 * Note: Descope's AuthProvider handles token refresh automatically.
 * This interceptor is a safety net for edge cases (expired tokens, etc.).
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableConfig | undefined;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshSubscribers.push((token) => {
            if (!token) return reject(error);
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(apiClient(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { refreshToken, clearSession } = useAuthStore.getState();

        if (!refreshToken) {
          clearSession();
          if (typeof window !== "undefined") {
            window.location.href = "/login";
          }
          return Promise.reject(error);
        }

        // Attempt Descope session refresh using the SDK.
        const refreshResult = await descopeRefresh(refreshToken);

        if (refreshResult?.data?.sessionJwt) {
          const newSession = refreshResult.data.sessionJwt;
          const newRefresh = refreshResult.data.refreshJwt ?? refreshToken;
          useAuthStore.getState().setSession(newSession, newRefresh);
          isRefreshing = false;
          flushRefreshSubscribers(newSession);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newSession}`;
          }
          return apiClient(originalRequest);
        }

        // Refresh failed — clear session.
        clearSession();
        isRefreshing = false;
        flushRefreshSubscribers(null);
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      } catch (refreshError) {
        const { clearSession } = useAuthStore.getState();
        clearSession();
        isRefreshing = false;
        flushRefreshSubscribers(null);
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      }
    }

    if (isAuthEndpoint(originalRequest?.url)) {
      return Promise.reject(error);
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
      // Distinguish between actual network failures and request timeouts / aborts.
      const isTimeout = error.code === "ECONNABORTED" || error.message?.includes("timeout");
      const isParseError =
        error.code === "ERR_BAD_RESPONSE" ||
        error.code === "ERR_PARSE_RESPONSE";
      const isAbort = error.code === "ERR_CANCELED";
      if (!isParseError && !isTimeout && !isAbort) {
        toast.add({
          title: "Network Error",
          description:
            "Could not connect to the server. Please check that the backend is running.",
          type: "error",
        });
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
    config?: InternalAxiosRequestConfig,
  ): Promise<T> => {
    const response = await apiClient.get<T>(url, config);
    return response.data;
  },
  post: <T>(url: string, data?: unknown, config?: InternalAxiosRequestConfig) =>
    withBody<T>("post", url, data, config),
  put: <T>(url: string, data?: unknown, config?: InternalAxiosRequestConfig) =>
    withBody<T>("put", url, data, config),
  patch: <T>(url: string, data?: unknown, config?: InternalAxiosRequestConfig) =>
    withBody<T>("patch", url, data, config),
  delete: async <T>(
    url: string,
    config?: InternalAxiosRequestConfig,
  ): Promise<T> => {
    const response = await apiClient.delete<T>(url, {
      ...config,
      // Ensure axios doesn't try to JSON.parse an empty 204 body.
      responseType: config?.responseType ?? "text",
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
