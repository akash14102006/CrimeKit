"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";
import { authService } from "@/services/authService";

const CURRENT_USER_KEY = ["auth", "current-user"] as const;

/**
 * Fetches the current user profile from the backend.
 *
 * The backend validates the Descope JWT, extracts the user identity,
 * and returns the locally-synced user record with roles and permissions.
 *
 * Falls back to Descope-provided user info during loading (no flicker).
 */
export function useCurrentUser() {
  const { sessionToken, isAuthenticated, setUser, user } = useAuthStore();

  const query = useQuery({
    queryKey: CURRENT_USER_KEY,
    queryFn: async () => {
      const profile = await authService.me();
      return profile;
    },
    enabled: isAuthenticated && !!sessionToken,
    staleTime: 5 * 60 * 1000,
    retry: (failureCount, error) => {
      const status = (error as { status?: number })?.status;
      if (status === 401 || status === 403) return false;
      return failureCount < 2;
    },
  });

  // Sync the fetched profile back to the auth store, preserving rich display names.
  useEffect(() => {
    if (query.data) {
      const existingName = user?.name?.trim();
      const backendName = query.data.name?.trim();
      const email = query.data.email || user?.email || "";
      const emailPrefix = email.includes("@") ? email.split("@")[0].toLowerCase() : "";

      const isGoodName = (n: string | undefined): boolean =>
        Boolean(n && !n.includes("@") && (!emailPrefix || n.toLowerCase() !== emailPrefix) && n !== "Investigator");

      let resolvedName = backendName;
      if (!isGoodName(backendName) && isGoodName(existingName)) {
        resolvedName = existingName;
      } else if (!resolvedName) {
        resolvedName = existingName || email || "Investigator";
      }

      setUser({
        ...query.data,
        name: resolvedName,
      });
    }
  }, [query.data, setUser, user?.name, user?.email]);

  const resolvedUser = query.data
    ? {
        ...query.data,
        name:
          query.data.name && !query.data.name.includes("@") && query.data.name !== "Investigator"
            ? query.data.name
            : user?.name || query.data.name || "Investigator",
      }
    : user;

  return {
    user: resolvedUser,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
}

/**
 * Invalidates the current user query. Call this on logout or role change.
 */
export function useInvalidateCurrentUser() {
  const { clearSession } = useAuthStore();
  return () => {
    clearSession();
  };
}
