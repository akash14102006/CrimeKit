"use client";

import { useCallback, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useSession, useDescope } from "@descope/react-sdk";
import { useAuthStore } from "@/store/authStore";

const IDLE_TIMEOUT_MS = 30 * 60 * 1000;

export function useAuthSession() {
  const router = useRouter();
  const { isAuthenticated } = useSession();
  const { logout: descopeLogout } = useDescope();
  const { clearSession } = useAuthStore();
  const idleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimers = useCallback(() => {
    if (idleTimerRef.current) {
      clearTimeout(idleTimerRef.current);
      idleTimerRef.current = null;
    }
  }, []);

  const handleLogout = useCallback(() => {
    clearTimers();
    clearSession();
    try { descopeLogout(); } catch {}
    router.push("/login");
  }, [clearTimers, clearSession, descopeLogout, router]);

  useEffect(() => {
    if (!isAuthenticated) return;

    function resetIdleTimer() {
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
      idleTimerRef.current = setTimeout(handleLogout, IDLE_TIMEOUT_MS);
    }

    const events = ["mousedown", "keydown", "scroll", "touchstart"];
    const handler = () => resetIdleTimer();

    events.forEach((e) => document.addEventListener(e, handler, { passive: true }));
    resetIdleTimer();

    return () => {
      events.forEach((e) => document.removeEventListener(e, handler));
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    };
  }, [isAuthenticated, handleLogout]);

  useEffect(() => () => clearTimers(), [clearTimers]);
}
