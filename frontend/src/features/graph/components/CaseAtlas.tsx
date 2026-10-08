"use client";

import React, { useState } from "react";
import { useCases } from "@/hooks/queries/useCases";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  FolderLock,
  Search,
  ArrowRight,
  ShieldAlert,
  Database,
  Network,
  Clock,
  Sparkles,
  RefreshCw,
  FolderOpen,
} from "lucide-react";

import type { CaseOut } from "@/types/case";
import { IsometricLoader } from "@/components/shared/IsometricLoader";

interface Props {
  onSelectCase: (caseId: string) => void;
}

export function CaseAtlas({ onSelectCase }: Props) {
  const { data: casesData, isLoading, isError, error, refetch } = useCases();
  const [search, setSearch] = useState<string>("");

  const cases: CaseOut[] = casesData?.items ?? [];

  const filteredCases = cases.filter((c: CaseOut) => {
    if (!search) return true;
    const q = search.toLowerCase();
    const matchName = (c.title || "").toLowerCase().includes(q);
    const matchId = (c.id || "").toLowerCase().includes(q);
    return matchName || matchId;
  });

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-background text-foreground p-6 overflow-y-auto">
      {/* Header Banner */}
      <div className="max-w-5xl mx-auto w-full space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
          <div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/30 font-mono text-[10px] uppercase">
                <FolderLock className="h-3 w-3 mr-1" />
                Case Atlas &bull; Forensic Graph Gateway
              </Badge>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-foreground mt-1">
              Select Investigation Workspace
            </h2>
            <p className="text-sm text-muted-foreground">
              Choose an authorized case to enter its interactive 3D Knowledge Graph environment
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative w-64">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filter cases by title, ID..."
                className="h-8 pl-8 pr-3 text-xs bg-card border-border text-foreground"
              />
            </div>
            <Button variant="outline" size="sm" className="h-8 border-border bg-card text-foreground" onClick={() => refetch()}>
              <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>

        {/* Case Cards Grid */}
        {isLoading ? (
          <div
            role="status"
            aria-busy="true"
            aria-live="polite"
            className="py-16 flex flex-col items-center justify-center text-center text-muted-foreground space-y-4 min-h-[320px]"
          >
            <IsometricLoader size={32} />
            <p className="text-sm font-medium text-muted-foreground">
              Loading authorized investigation cases...
            </p>
          </div>
        ) : isError ? (
          <div className="py-16 flex flex-col items-center justify-center text-center text-muted-foreground space-y-4 border border-border rounded-lg bg-card/40 min-h-[320px]">
            <ShieldAlert className="h-10 w-10 mx-auto text-destructive" />
            <div className="space-y-1">
              <p className="text-sm font-semibold text-foreground">Failed to load investigation cases</p>
              <p className="text-xs text-muted-foreground">
                {(error as Error)?.message || "A network or authorization error occurred while fetching cases."}
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              className="border-border bg-card text-foreground mt-1"
            >
              Retry
            </Button>
          </div>
        ) : filteredCases.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredCases.map((c: CaseOut) => {
              const caseId = c.id;
              const title = c.title || `Investigation ${caseId}`;
              const status = (c.status || "OPEN").toUpperCase();

              return (
                <Card
                  key={caseId}
                  className="bg-card hover:bg-accent/50 border-border hover:border-sky-500/50 transition-all cursor-pointer group shadow-md flex flex-col justify-between"
                  onClick={() => onSelectCase(caseId)}
                >
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className="text-[10px] font-mono bg-muted text-muted-foreground border-border">
                        {caseId.slice(0, 12)}
                      </Badge>
                      <Badge className={status === "OPEN" ? "bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border-emerald-500/30" : "bg-muted text-muted-foreground"}>
                        {status}
                      </Badge>
                    </div>
                    <CardTitle className="text-base font-semibold text-foreground group-hover:text-sky-500 transition-colors mt-2 line-clamp-1">
                      {title}
                    </CardTitle>
                    <CardDescription className="text-xs text-muted-foreground line-clamp-2 mt-1">
                      {c.description || "Active digital forensics & evidence correlation case"}
                    </CardDescription>
                  </CardHeader>

                  <CardContent className="p-4 pt-3 border-t border-border mt-2">
                    <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
                      <div className="flex items-center gap-1.5 text-foreground">
                        <Network className="h-3.5 w-3.5 text-sky-500" />
                        <span>3D Knowledge Graph</span>
                      </div>
                      <div className="flex items-center gap-1 text-sky-600 dark:text-sky-400 font-semibold group-hover:translate-x-1 transition-transform">
                        <span>Enter Scene</span>
                        <ArrowRight className="h-3.5 w-3.5" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        ) : (
          <div className="py-16 text-center text-muted-foreground space-y-4 border border-border rounded-lg bg-card/40">
            <FolderOpen className="h-10 w-10 mx-auto text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-semibold text-foreground">No authorized cases found</p>
              <p className="text-xs text-muted-foreground">Create a case in Case Management or verify your RBAC permissions.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
