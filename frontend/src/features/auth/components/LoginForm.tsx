"use client";

import dynamic from "next/dynamic";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useCallback, useRef, useState } from "react";
import { Loader2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuthStore, DEV_ADMIN_PROFILE, DEV_ADMIN_TOKEN } from "@/store/authStore";
import { env } from "@/config/env";
import { extractDisplayName } from "@/lib/userDisplay";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";

const DescopeFlow = dynamic(
  () =>
    import("@descope/react-sdk").then((m) => {
      const Descope = m.Descope;
      return function LoginDescope(
        props: React.ComponentProps<typeof Descope>,
      ) {
        return <Descope {...props} />;
      };
    }),
  {
    ssr: false,
    loading: () => (
      <div className="flex flex-col items-center justify-center py-8 gap-3">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Loading identity provider...</p>
      </div>
    ),
  },
);

import { authService } from "@/services/authService";

/**
 * LoginForm — CrimeKit Enterprise Authentication.
 * Powered exclusively by Enterprise Identity Provider (Descope).
 */
export function LoginForm() {
  const router = useRouter();
  const { setSession, setUser, markSessionResolved } = useAuthStore();
  const navigated = useRef(false);
  const [error, setError] = useState("");
  const [isLoggingInDev, setIsLoggingInDev] = useState(false);

  const handleExplicitDemoLogin = useCallback(async () => {
    if (navigated.current || isLoggingInDev) return;
    setIsLoggingInDev(true);
    setError("");

    try {
      const resp = await authService.login("admin@crimekit.local");
      if (resp?.access_token) {
        setSession(resp.access_token, resp.refresh_token ?? null);
        if (resp.user) {
          setUser(resp.user);
        } else {
          setUser(DEV_ADMIN_PROFILE);
        }
        markSessionResolved();
        navigated.current = true;
        router.replace("/dashboard");
      } else {
        setError("Login response did not include a valid session token.");
      }
    } catch (err) {
      console.error("[CrimeKit] Explicit demo login failed:", err);
      setError("Unable to authenticate with development credentials. Ensure backend is running.");
    } finally {
      setIsLoggingInDev(false);
    }
  }, [router, setSession, setUser, markSessionResolved, isLoggingInDev]);

  const handleSuccess = useCallback(
    (
      event: CustomEvent<{
        sessionJwt?: string;
        access_token?: string;
        refreshJwt?: string;
        refresh_token?: string;
      }>,
    ) => {
      if (navigated.current) return;

      const detail = event?.detail;
      const sessionJwt = detail?.sessionJwt || detail?.access_token;
      const refreshJwt = detail?.refreshJwt || detail?.refresh_token;

      if (!sessionJwt) {
        console.error(
          "[CrimeKit] onSuccess fired but no session token in event detail:",
          detail,
        );
        setError("Login succeeded but no session token was received.");
        return;
      }

      setSession(sessionJwt, refreshJwt ?? null);

      // Extract user info from the JWT payload
      try {
        const payload = JSON.parse(atob(sessionJwt.split(".")[1]));
        const defaultRole = "jury_evaluator";
        const roles: string[] =
          Array.isArray(payload.roles) && payload.roles.length > 0
            ? payload.roles
            : [defaultRole];
        setUser({
          id: payload.sub || "unknown",
          email: payload.email || "",
          name: extractDisplayName(payload, "Investigator"),
          role: (roles[0] || defaultRole) as
            | "admin"
            | "investigator"
            | "analyst"
            | "evidence_officer"
            | "compliance_officer"
            | "auditor"
            | "viewer"
            | "demo_evaluator"
            | "jury_evaluator"
            | "user",
          roles: roles as (
            | "admin"
            | "investigator"
            | "analyst"
            | "evidence_officer"
            | "compliance_officer"
            | "auditor"
            | "viewer"
            | "demo_evaluator"
            | "jury_evaluator"
            | "user"
          )[],
          permissions: [],
          is_active: true,

          organization: "CrimeKit Enterprise",
          tenant: "default",
        });
      } catch {
        // JWT decode fallback — backend /auth/me will synchronize full profile
      }

      markSessionResolved();
      navigated.current = true;
      router.push("/dashboard");
    },
    [router, setSession, setUser, markSessionResolved],
  );

  const handleError = useCallback((event: CustomEvent) => {
    console.error("[CrimeKit] Identity provider error:", event);
    const detail = event?.detail;
    const errText = (
      typeof detail === "string"
        ? detail
        : detail?.error || detail?.errorMessage || detail?.message || ""
    ).toLowerCase();

    // Sanitize error: never expose internal [E062108] or raw technical errors to users
    if (
      errText.includes("e062108") ||
      errText.includes("user not found") ||
      errText.includes("does not exist") ||
      errText.includes("unauthorized login attempt")
    ) {
      setError(
        "We couldn't complete your sign-in. Please ensure you are using an authorized institutional account or contact your system administrator.",
      );
    } else if (errText.includes("popup") || errText.includes("cancelled") || errText.includes("closed")) {
      setError("Sign-in was cancelled or the window was closed. Please try again.");
    } else {
      setError(
        "Authentication service encountered an issue. Please try again or contact support.",
      );
    }
  }, []);

  return (
    <Card className="w-[420px] shadow-xl border-t-4 border-t-primary">
      <CardHeader className="space-y-1 text-center">
        <div className="flex justify-center mb-4">
          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Image
              src="/crimekit-logo.png"
              alt="CrimeKit"
              width={24}
              height={24}
              className="h-6 w-6 object-contain"
              priority
            />
          </div>
        </div>
        <CardTitle className="text-2xl tracking-tight">
          CrimeKit Enterprise
        </CardTitle>
        <CardDescription>
          Sign in to access the secure investigation workspace
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 rounded-md bg-destructive/15 border border-destructive/20 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <DescopeFlow
          flowId={env.descopeFlowId}
          onSuccess={handleSuccess}
          onError={handleError}
          theme="dark"
        />

        {(env.devAuthDisabled || env.authDemoMode || env.demoMode) && (
          <div className="mt-4 pt-4 border-t border-border">
            <Button
              type="button"
              variant="default"
              disabled={isLoggingInDev}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium"
              onClick={handleExplicitDemoLogin}
            >
              {isLoggingInDev ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Authenticating...
                </>
              ) : (
                "Demo / Evaluator Quick Access"
              )}
            </Button>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-center border-t p-4 mt-4">
        <p className="text-sm text-muted-foreground">
          Authorized personnel only. All access is logged.
        </p>
      </CardFooter>
    </Card>
  );
}
