"use client";

import Link from "next/link";
import { Briefcase, Clock, ArrowRight, AlertTriangle, RefreshCw } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useCases } from "@/hooks/queries/useCases";
import { useRBAC } from "@/hooks/useRBAC";
import { getErrorMessage } from "@/lib/api-client";

function CaseSkeleton() {
  return (
    <div className="flex items-center justify-between p-3 border rounded-lg">
      <div className="flex items-center space-x-3">
        <Skeleton className="h-8 w-8 rounded-full" />
        <div className="space-y-1">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-20" />
        </div>
      </div>
      <Skeleton className="h-5 w-16 rounded" />
    </div>
  );
}

export function ActiveCases() {
  const { data, isLoading, isError, error, refetch } = useCases({ page: 1, limit: 100 });
  const cases = data?.items;
  const { hasPermission } = useRBAC();

  const canViewCases = hasPermission("case:read");
  const activeCases = cases?.filter((c) => c.status !== "closed") ?? [];

  if (!canViewCases) {
    return null;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base">Active Cases</CardTitle>
          <CardDescription>
            {isLoading ? "Loading..." : `${activeCases.length} open investigation${activeCases.length !== 1 ? "s" : ""}`}
          </CardDescription>
        </div>
        <Link href="/cases">
          <Button variant="ghost" size="sm">
            View All <ArrowRight className="h-3 w-3 ml-1" />
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {isError ? (
          <div className="flex flex-col items-center justify-center py-6">
            <AlertTriangle className="h-6 w-6 text-destructive mb-2" />
            <p className="text-sm text-muted-foreground mb-2">
              {error ? getErrorMessage(error) : "Failed to load cases"}
            </p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </div>
        ) : isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <CaseSkeleton key={i} />
            ))}
          </div>
        ) : activeCases.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <Briefcase className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">No active cases</p>
            <p className="text-xs text-muted-foreground mt-1">
              Create a new case to get started
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {activeCases.slice(0, 5).map((c) => (
              <Link
                key={c.id}
                href={`/workspace/${c.id}`}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors group"
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <div className="bg-primary/10 p-2 rounded-full shrink-0">
                    <Briefcase className="h-4 w-4 text-primary" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate group-hover:text-primary transition-colors">
                      {c.title}
                    </p>
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {c.id.slice(0, 8)}
                    </p>
                  </div>
                </div>
                <Badge
                  variant={
                    c.status === "open"
                      ? "default"
                      : c.status === "review"
                        ? "secondary"
                        : "outline"
                  }
                  className="shrink-0 ml-2"
                >
                  {c.status}
                </Badge>
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
