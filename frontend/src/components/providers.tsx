"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toast";
import { TooltipProvider } from "@/components/ui/tooltip";
import { queryDefaults } from "@/config/query";
import { DescopeProviderWrapper } from "@/components/auth/DescopeProviderWrapper";
import { DescopeErrorBoundary } from "@/components/auth/DescopeErrorBoundary";

const queryClient = new QueryClient(queryDefaults);
if (typeof window !== "undefined") {
  (window as unknown as Record<string, unknown>).__queryClient = queryClient;
}

import { useAuthSession } from "@/hooks/useAuthSession";
import { useDescopeSessionSync } from "@/hooks/useDescopeSessionSync";

function SessionManager() {
  useAuthSession();
  useDescopeSessionSync();
  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <DescopeProviderWrapper>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider>
            <DescopeErrorBoundary fallback={null}>
              <SessionManager />
            </DescopeErrorBoundary>
            {children}
            <Toaster />
          </TooltipProvider>
        </QueryClientProvider>
      </DescopeProviderWrapper>
    </NextThemesProvider>
  );
}
