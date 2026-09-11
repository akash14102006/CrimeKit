"use client";

import { useEffect, useState } from "react";

interface UseLocalStorageReturn<T> {
  value: T | undefined;
  setValue: (value: T) => void;
  removeValue: () => void;
}

/** useState backed by localStorage with a stable setter API. */
export function useLocalStorage<T>(key: string): UseLocalStorageReturn<T> {
  const [value, setValueState] = useState<T | undefined>(() => {
    if (typeof window === "undefined") return undefined;
    try {
      const raw = window.localStorage.getItem(key);
      return raw ? (JSON.parse(raw) as T) : undefined;
    } catch {
      return undefined;
    }
  });

  useEffect(() => {
    if (value === undefined) return;
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Ignore quota/security errors in private browsing.
    }
  }, [key, value]);

  const setValue = (next: T) => setValueState(next);
  const removeValue = () => {
    if (typeof window !== "undefined") window.localStorage.removeItem(key);
    setValueState(undefined);
  };

  return { value, setValue, removeValue };
}
