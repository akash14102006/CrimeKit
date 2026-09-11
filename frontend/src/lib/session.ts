/** Browser session helpers used by auth flows. */

const SESSION_STORAGE_KEY = "crimekit-pending-mfa";

export function storePendingEmail(email: string) {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(SESSION_STORAGE_KEY, email);
}

export function getPendingEmail(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(SESSION_STORAGE_KEY);
}

export function clearPendingEmail() {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(SESSION_STORAGE_KEY);
}

/**
 * Clear all Descope-related storage on logout.
 */
export function clearAllAuthStorage() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("crimekit-ds-session");
  localStorage.removeItem("crimekit-ds-refresh");
  localStorage.removeItem("crimekit-auth");
  sessionStorage.removeItem(SESSION_STORAGE_KEY);
}
