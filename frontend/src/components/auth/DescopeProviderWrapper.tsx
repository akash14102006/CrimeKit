"use client";

import * as React from "react";
import { AuthProvider } from "@descope/react-sdk";
import { env } from "@/config/env";
import { DescopeErrorBoundary } from "./DescopeErrorBoundary";

export function DescopeProviderWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const projectId = env.descopeProjectId || "P3FF4lAVyrTtQeqlbuAeSdoCbrIX";

  return (
    <DescopeErrorBoundary fallback={<>{children}</>}>
      <React.Suspense fallback={<div className="flex min-h-screen items-center justify-center">Loading...</div>}>
        <AuthProvider
          projectId={projectId}
          refreshCookieName="crimekit-ds-refresh"
          sessionTokenViaCookie={{ secure: process.env.NODE_ENV !== "development" }}
          refreshTokenViaCookie={{ secure: process.env.NODE_ENV !== "development" }}
          persistTokens
          storeLastAuthenticatedUser
        >
          {children}
        </AuthProvider>
      </React.Suspense>
    </DescopeErrorBoundary>
  );
}
