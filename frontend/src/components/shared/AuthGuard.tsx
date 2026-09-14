"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { useHasHydrated } from "@/hooks/useHasHydrated";
import { Loader2 } from "lucide-react";

interface AuthGuardProps {
  children: React.ReactNode;
  /** If provided, user must have at least one of these roles to access this page. */
  allowedRoles?: string[];
}

/**
 * AuthGuard — Enterprise RBAC route guard.
 *
 * Auth state source of truth: Zustand store (set by LoginForm onSuccess or
 * useDescopeSessionSync). We do NOT depend on useSession() from the Descope
 * SDK because its React context update is asynchronous and can cause redirect
 * loops with stale false values.
 */
export function AuthGuard({ children, allowedRoles }: AuthGuardProps) {
  const router = useRouter();
  const { isAuthenticated, sessionToken, user, sessionResolved } = useAuthStore();
  const hydrated = useHasHydrated(useAuthStore);

  const isAuth = isAuthenticated && !!sessionToken;
  const userRoles = (user?.roles as string[]) ?? (user?.role ? [user.role] : []);
  const isJury = userRoles.includes("jury_evaluator") || userRoles.includes("demo_evaluator");
  const isStrictAdminOnly = !!allowedRoles && allowedRoles.length === 1 && allowedRoles[0] === "admin";
  const authorized = isAuth && (!allowedRoles || (isJury && !isStrictAdminOnly) || (!!user && allowedRoles.some((r) => userRoles.includes(r))));


  useEffect(() => {
    if (!hydrated || !sessionResolved) return;
    if (authorized) return;

    const href = !isAuth ? "/login" : "/forbidden";
    router.replace(href);
  }, [hydrated, sessionResolved, authorized, isAuth, router]);

  if (!hydrated || !sessionResolved) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!authorized) {
    return null;
  }

  return <>{children}</>;
}
