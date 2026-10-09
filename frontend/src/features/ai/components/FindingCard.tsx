"use client";

import React from "react";
import type { AIFinding } from "../store/aiStore";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getAgent } from "../constants/agentRegistry";
import { ShieldCheck, AlertTriangle, HelpCircle, FileText, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface FindingCardProps {
  finding: AIFinding;
  onViewEvidence?: (evidenceId: string) => void;
  onHandoff?: (targetAgentId: import("../constants/agentRegistry").AgentId, finding: AIFinding) => void;
  className?: string;
}

export function FindingCard({ finding, onViewEvidence, onHandoff, className }: FindingCardProps) {
  const agent = getAgent(finding.agentId);

  const statusConfig = {
    verified: {
      label: "Verified Lead",
      badgeClass: "bg-emerald-500/15 text-emerald-600 border-emerald-500/30",
      icon: <ShieldCheck className="h-3 w-3 text-emerald-500" />,
    },
    "needs-review": {
      label: "Needs Review",
      badgeClass: "bg-amber-500/15 text-amber-600 border-amber-500/30",
      icon: <AlertTriangle className="h-3 w-3 text-amber-500" />,
    },
    inconclusive: {
      label: "Inconclusive",
      badgeClass: "bg-muted text-muted-foreground border-border",
      icon: <HelpCircle className="h-3 w-3 text-muted-foreground" />,
    },
  }[finding.status];

  return (
    <div
      className={cn(
        "rounded-lg border bg-card p-3 text-card-foreground shadow-sm my-2.5 space-y-2.5",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="space-y-0.5">
          <div className="flex items-center gap-1.5">
            <span title={agent.name}>
              {(() => {
                const Icon = agent.icon;
                return <Icon className="h-3 w-3 text-primary stroke-[1.8]" aria-hidden="true" />;
              })()}
            </span>
            <span className="text-[11px] font-medium text-muted-foreground">
              {agent.shortName}
            </span>
            <span className="text-muted-foreground/40">•</span>
            <div className="flex items-center gap-1">
              {statusConfig.icon}
              <span className="text-[11px] font-medium text-muted-foreground">
                {statusConfig.label}
              </span>
            </div>
          </div>
          <h4 className="text-sm font-semibold tracking-tight text-foreground">
            {finding.title}
          </h4>
        </div>

        <div className="flex flex-col items-end shrink-0">
          <Badge variant="outline" className="text-[11px] font-mono font-semibold">
            {(finding.confidence * 100).toFixed(0)}% Conf
          </Badge>
        </div>
      </div>

      <p className="text-xs text-muted-foreground leading-relaxed">
        {finding.description}
      </p>

      {/* Supporting Evidence references */}
      {finding.evidenceRefs && finding.evidenceRefs.length > 0 && (
        <div className="pt-2 border-t flex flex-wrap items-center gap-1.5">
          <span className="text-[10px] uppercase font-semibold text-muted-foreground mr-1">
            Evidence:
          </span>
          {finding.evidenceRefs.map((ref) => (
            <button
              key={ref}
              type="button"
              onClick={() => onViewEvidence?.(ref)}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-muted hover:bg-muted/80 text-foreground transition-colors border"
            >
              <FileText className="h-2.5 w-2.5 text-muted-foreground" />
              <span>{ref.length > 12 ? `${ref.slice(0, 8)}...` : ref}</span>
            </button>
          ))}
        </div>
      )}

      {/* Action / Handoff Buttons */}
      <div className="pt-2 border-t flex flex-wrap items-center gap-1.5">
        {finding.evidenceRefs && finding.evidenceRefs[0] && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="h-6 text-[10px] px-2 gap-1"
            onClick={() => onViewEvidence?.(finding.evidenceRefs[0])}
          >
            <FileText className="h-2.5 w-2.5 text-primary" />
            Open Evidence
          </Button>
        )}

        {onHandoff && finding.agentId !== "timeline" && (
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="h-6 text-[10px] px-2 gap-1 text-foreground"
            onClick={() => onHandoff("timeline", finding)}
          >
            <span>Send to Timeline</span>
            <ArrowRight className="h-2.5 w-2.5" />
          </Button>
        )}

        {onHandoff && finding.agentId !== "geoscope" && (
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="h-6 text-[10px] px-2 gap-1 text-foreground"
            onClick={() => onHandoff("geoscope", finding)}
          >
            <span>Send to GeoScope</span>
            <ArrowRight className="h-2.5 w-2.5" />
          </Button>
        )}

        {onHandoff && finding.agentId !== "testimony" && (
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="h-6 text-[10px] px-2 gap-1 text-foreground"
            onClick={() => onHandoff("testimony", finding)}
          >
            <span>Send to Testimony</span>
            <ArrowRight className="h-2.5 w-2.5" />
          </Button>
        )}
      </div>
    </div>
  );
}
