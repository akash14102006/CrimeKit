"use client";

import React from "react";
import type { AgentHandoff } from "../store/aiStore";
import { getAgent, type AgentId } from "../constants/agentRegistry";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface AgentHandoffCardProps {
  handoff: AgentHandoff;
  onAcceptHandoff: (targetAgentId: AgentId) => void;
  className?: string;
}

export function AgentHandoffCard({
  handoff,
  onAcceptHandoff,
  className,
}: AgentHandoffCardProps) {
  const targetAgent = getAgent(handoff.targetAgentId);

  return (
    <div
      className={cn(
        "rounded-lg border border-primary/30 bg-primary/5 p-3 text-xs my-2.5 space-y-2",
        className,
      )}
    >
      <div className="flex items-center gap-1.5 text-primary font-medium text-[11px]">
        <Sparkles className="h-3 w-3" />
        <span>Specialist Agent Recommendation</span>
      </div>

      <p className="text-muted-foreground leading-relaxed">
        {handoff.reason}
      </p>

      <div className="pt-1 flex items-center justify-between">
        <div className="flex items-center gap-1.5 font-medium text-foreground">
          {(() => {
            const Icon = targetAgent.icon;
            return <Icon className="h-4 w-4 text-primary stroke-[1.8]" aria-hidden="true" />;
          })()}
          <span>{targetAgent.name}</span>
        </div>

        <Button
          type="button"
          size="sm"
          variant="default"
          onClick={() => onAcceptHandoff(handoff.targetAgentId)}
          className="h-7 text-xs gap-1.5 px-2.5"
        >
          <span>Continue with {targetAgent.shortName}</span>
          <ArrowRight className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}
