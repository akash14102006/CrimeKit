"use client";

import { useSyncExternalStore } from "react";
import type { StoreApi } from "zustand";

/**
 * Tracks whether a persisted zustand store has finished hydrating from
 * localStorage. Avoids setState-in-effect; SSR renders as false.
 */
export function useHasHydrated<State>(store: StoreApi<State> & {
  persist: { hasHydrated: () => boolean; onFinishHydration: (fn: () => void) => () => void };
}) {
  return useSyncExternalStore(
    (callback) => store.persist.onFinishHydration(callback),
    () => store.persist.hasHydrated(),
    () => false,
  );
}
