"use client";

import React from "react";
import { AGENT_LIST, type AgentId } from "../constants/agentRegistry";
import { cn } from "@/lib/utils";

interface AgentSelectorProps {
  selectedAgentId: AgentId;
  onSelectAgent: (agentId: AgentId) => void;
  className?: string;
}

export function AgentSelector({
  selectedAgentId,
  onSelectAgent,
  className,
}: AgentSelectorProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-1.5 overflow-x-auto py-2 px-3 bg-muted/30 border-b scrollbar-none",
        className,
      )}
      role="tablist"
      aria-label="Investigation Agent Selector"
    >
      <div className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider shrink-0 mr-2 flex items-center gap-1">
        <span>Agents</span>
      </div>

      {AGENT_LIST.filter((a) => a.id !== "evidence-review").map((agent) => {
        const isSelected = agent.id === selectedAgentId;
        const Icon = agent.icon;
        return (
          <button
            key={agent.id}
            role="tab"
            aria-selected={isSelected}
            aria-label={`${agent.name} — ${agent.tagline}`}
            onClick={() => onSelectAgent(agent.id)}
            className={cn(
              "group relative flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 shrink-0 border text-left cursor-pointer",
              isSelected
                ? "bg-background text-foreground border-primary/80 shadow-sm ring-1 ring-primary/30"
                : "bg-background/60 text-muted-foreground border-border/60 hover:bg-background hover:text-foreground hover:border-primary/40",
            )}
          >
            <span
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-md shrink-0 transition-transform duration-200 group-hover:scale-[1.03]",
                isSelected
                  ? "bg-primary/10 text-primary border border-primary/20 shadow-xs"
                  : "bg-muted/60 text-muted-foreground border border-border/40 group-hover:bg-muted group-hover:text-foreground",
              )}
            >
              <Icon
                className={cn(
                  "h-5 w-5 transition-colors",
                  isSelected ? "text-primary stroke-[2]" : "text-muted-foreground group-hover:text-foreground stroke-[1.8]",
                )}
                aria-hidden="true"
              />
            </span>
            <div className="flex flex-col min-w-0 pr-1">
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-foreground whitespace-nowrap">
                  {agent.name.replace(" Agent", "")}
                </span>
                {isSelected && (
                  <span
                    className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"
                    aria-label="Active status indicator"
                  />
                )}
              </div>
              <span className="text-[10px] text-muted-foreground truncate max-w-[150px]">
                {agent.tagline}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
