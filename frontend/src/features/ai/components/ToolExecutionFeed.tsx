"use client";

import React, { useState } from "react";
import type { ToolExecution } from "../store/aiStore";
import { Check, Loader2, Clock, AlertCircle, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface ToolExecutionFeedProps {
  executions: ToolExecution[];
  className?: string;
}

export function ToolExecutionFeed({ executions, className }: ToolExecutionFeedProps) {
  const [expanded, setExpanded] = useState(false);

  if (!executions || executions.length === 0) return null;

  const runningCount = executions.filter((e) => e.status === "running").length;
  const completedCount = executions.filter((e) => e.status === "completed").length;
  const isAllDone = runningCount === 0 && completedCount === executions.length;

  return (
    <div
      className={cn(
        "rounded-md border bg-muted/20 text-xs overflow-hidden transition-all my-2.5",
        className,
      )}
    >
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-muted/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          {runningCount > 0 ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
          ) : (
            <Check className="h-3.5 w-3.5 text-emerald-500" />
          )}
          <span className="font-medium text-foreground">
            {runningCount > 0
              ? `Agent executing tools (${runningCount} active)...`
              : `Tool executions completed (${completedCount}/${executions.length})`}
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-muted-foreground text-[11px]">
          <span>{expanded ? "Hide" : "Details"}</span>
          {expanded ? (
            <ChevronUp className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
        </div>
      </button>

      {/* Expanded list of each tool step */}
      {expanded && (
        <div className="border-t divide-y bg-background/50 px-3 py-1 text-[11px]">
          {executions.map((exec) => {
            const isTavily = exec.tool === "tavily_web_research" || exec.label?.toLowerCase().includes("tavily");
            return (
              <div
                key={exec.id}
                className="py-1.5 space-y-1"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 min-w-0">
                    {exec.status === "completed" && (
                      <Check className="h-3 w-3 text-emerald-500 shrink-0" />
                    )}
                    {exec.status === "running" && (
                      <Loader2 className="h-3 w-3 animate-spin text-primary shrink-0" />
                    )}
                    {exec.status === "pending" && (
                      <Clock className="h-3 w-3 text-muted-foreground shrink-0" />
                    )}
                    {exec.status === "failed" && (
                      <AlertCircle className="h-3 w-3 text-destructive shrink-0" />
                    )}
                    <span
                      className={cn(
                        "truncate font-medium",
                        exec.status === "completed" && "text-foreground",
                        exec.status === "running" && "text-primary font-semibold",
                        exec.status === "failed" && "text-destructive",
                      )}
                    >
                      {exec.label}
                    </span>
                  </div>
                  <span className="text-[10px] text-muted-foreground font-mono uppercase shrink-0 ml-2">
                    {exec.status}
                  </span>
                </div>

                {/* Specialized Tavily Web Research card */}
                {isTavily && exec.outputSnippet && (
                  <div className="rounded border bg-primary/5 p-2 text-[10px] space-y-1 text-muted-foreground">
                    <div className="flex items-center justify-between font-mono">
                      <span className="font-semibold text-primary">Tavily Web Research</span>
                      <span className="text-[9px] bg-amber-500/10 text-amber-600 px-1 py-0.2 rounded border border-amber-500/20">
                        EXTERNAL WEB SOURCE
                      </span>
                    </div>
                    <p className="line-clamp-2 text-foreground font-sans">
                      {exec.outputSnippet}
                    </p>
                    <div className="text-[9px] text-muted-foreground">
                      Provenance verified • External contextual intelligence
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
