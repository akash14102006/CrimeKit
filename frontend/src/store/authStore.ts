import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { UserProfile } from "@/types/auth";

const SESSION_BROADCAST_KEY = "crimekit-session-event";

function broadcastLogout() {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(
      SESSION_BROADCAST_KEY,
      JSON.stringify({ type: "logout", ts: Date.now() }),
    );
  } catch {
    // Private browsing — ignore.
  }
}

interface AuthState {
  user: UserProfile | null;
  sessionToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  sessionResolved: boolean;

  setSession: (sessionToken: string, refreshToken: string | null) => void;
  setUser: (user: UserProfile) => void;
  clearSession: () => void;
  markSessionResolved: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      sessionToken: null,
      refreshToken: null,
      isAuthenticated: false,
      sessionResolved: false,

      setSession: (sessionToken, refreshToken) =>
        set({
          sessionToken,
          refreshToken,
          isAuthenticated: !!sessionToken,
        }),

      setUser: (user) => set({ user }),

      clearSession: () => {
        set({
          user: null,
          sessionToken: null,
          refreshToken: null,
          isAuthenticated: false,
          sessionResolved: true,
        });
        if (typeof window !== "undefined") {
          try {
            localStorage.removeItem("crimekit-auth");
            localStorage.removeItem("crimekit-ds-session");
            localStorage.removeItem("crimekit-ds-refresh");
            localStorage.removeItem("crimekit-session");
            localStorage.removeItem("crimekit_user");
            sessionStorage.clear();

            // Clear cookies
            document.cookie.split(";").forEach((cookie) => {
              const eqPos = cookie.indexOf("=");
              const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
              document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;`;
              document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=${window.location.hostname};`;
            });
          } catch {
            // ignore storage errors
          }

          // Clear React Query cache to prevent stale data from previous session
          try {
            const w = window as unknown as Record<string, unknown>;
            if (w.__queryClient) {
              (w.__queryClient as { clear: () => void }).clear();
            }
          } catch {
            // Query client not available
          }
        }
        broadcastLogout();
      },

      markSessionResolved: () => set({ sessionResolved: true }),
    }),
    {
      name: "crimekit-auth",
      partialize: (state) => ({
        user: state.user,
        sessionToken: state.sessionToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);

// Cross-tab logout listener.
if (typeof window !== "undefined") {
  window.addEventListener("storage", (e) => {
    if (e.key === SESSION_BROADCAST_KEY && e.newValue) {
      try {
        const event = JSON.parse(e.newValue) as { type: string };
        if (event.type === "logout") {
          useAuthStore.getState().clearSession();
          window.location.href = "/login";
        }
      } catch {
        // Ignore malformed events.
      }
    }
  });
}
