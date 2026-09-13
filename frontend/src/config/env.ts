/**
 * Runtime configuration. Values are read from the environment at build time
 * (NEXT_PUBLIC_*) with safe fallbacks so the app boots in any environment.
 */

function hostname(): string {
  if (typeof window === "undefined") return "localhost";
  return window.location.hostname || "localhost";
}

export const env = {
  /** Backend base URL. Falls back to the current host on port 8002. */
  apiBaseUrl:
    process.env.NEXT_PUBLIC_API_URL ?? `http://${hostname()}:8002`,

  /** Public app URL (used for share links and canonical metadata). */
  appUrl:
    process.env.NEXT_PUBLIC_APP_URL ??
    (typeof window === "undefined"
      ? "http://localhost:3000"
      : window.location.origin),

  /** Auth provider project id (optional; fallback sentinel only). */
  descopeProjectId:
    process.env.NEXT_PUBLIC_DESCOPE_PROJECT_ID || "P3FF4lAVyrTtQeqlbuAeSdoCbrIX",

  /** Global request timeout in milliseconds. */
  requestTimeoutMs: Number(process.env.NEXT_PUBLIC_REQUEST_TIMEOUT_MS ?? 15_000),

  isProduction: process.env.NODE_ENV === "production",

  /** Whether demo/development authentication mode is active (allows any email & auto-provisioning). */
  authDemoMode:
    process.env.NEXT_PUBLIC_AUTH_DEMO_MODE !== undefined
      ? process.env.NEXT_PUBLIC_AUTH_DEMO_MODE === "true"
      : process.env.NODE_ENV !== "production",
} as const;
