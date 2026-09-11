"use client";

import { useCurrentUser } from "@/hooks/useCurrentUser";

/**
 * Mounts the current user query on dashboard load.
 * This ensures the user profile is fetched once and kept in sync
 * with the auth store. Renders nothing — just a data-fetching side effect.
 */
export function CurrentUserLoader() {
  useCurrentUser();
  return null;
}
