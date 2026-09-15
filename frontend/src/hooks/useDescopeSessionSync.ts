"use client";

import { useEffect, useRef } from "react";
import { useSession, useUser } from "@descope/react-sdk";
import { useAuthStore } from "@/store/authStore";
import { env } from "@/config/env";
import { extractDisplayName } from "@/lib/userDisplay";

/**
 * useDescopeSessionSync — bridges Descope's AuthProvider state into the Zustand auth store.
 *
 * Only syncs FROM Descope TO Zustand (push). Never clears Zustand based on
 * Descope's async context timing. Session expiry is handled by:
 * - useAuthSession (idle timeout)
 * - api-client interceptor (401 responses)
 * - explicit logout
 */
export function useDescopeSessionSync() {
  const { sessionToken, isAuthenticated: descopeAuthenticated } = useSession();
  const { user: descopeUser } = useUser();

  const { setSession, setUser, markSessionResolved } = useAuthStore();
  const hasResolved = useRef(false);
  const hasSyncedFromDescope = useRef(false);

  useEffect(() => {
    // When Descope confirms auth AND provides a token, sync to Zustand.
    if (descopeAuthenticated && sessionToken) {
      setSession(sessionToken, null);
      hasSyncedFromDescope.current = true;

      if (descopeUser) {
        const descopeRoles = (descopeUser as Record<string, unknown>).roles;
        const defaultRole = "jury_evaluator";
        const roles: string[] = Array.isArray(descopeRoles) && descopeRoles.length > 0
          ? descopeRoles.map((r: unknown) => {
              const str = String(r).toLowerCase().trim();
              if (str === "viewer" || str === "user" || str === "demo_evaluator") return "jury_evaluator";
              return str;
            })
          : [defaultRole];
        const primaryRole = roles[0] ?? defaultRole;
        setUser({
          id: descopeUser.userId ?? descopeUser.loginIds?.[0] ?? "unknown",
          email: descopeUser.email ?? descopeUser.phone ?? "",
          name: extractDisplayName(descopeUser as Record<string, unknown>, "Investigator"),
          role: primaryRole as "admin" | "investigator" | "analyst" | "evidence_officer" | "compliance_officer" | "auditor" | "viewer" | "demo_evaluator" | "jury_evaluator" | "user",
          roles: roles as ("admin" | "investigator" | "analyst" | "evidence_officer" | "compliance_officer" | "auditor" | "viewer" | "demo_evaluator" | "jury_evaluator" | "user")[],
          permissions: [],
          is_active: true,
          organization: "CrimeKit Enterprise",
          tenant: "default",
        });

      }
    }

    if (!hasResolved.current) {
      hasResolved.current = true;
      markSessionResolved();
    }
  }, [
    descopeAuthenticated,
    sessionToken,
    descopeUser,
    setSession,
    setUser,
    markSessionResolved,
  ]);
}
