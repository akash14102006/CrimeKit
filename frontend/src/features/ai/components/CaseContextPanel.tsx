"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  FolderKanban,
  FileText,
  Brain,
  GitBranch,
  CalendarClock,
  AlertTriangle,
  ExternalLink,
  ShieldCheck,
  Cpu,
  ArrowRight,
  Database,
} from "lucide-react";
import { useWorkspace, useWorkspaceProgress, useWorkspaceAIFindings } from "@/hooks/queries/useWorkspace";
import { getAgent, type AgentId } from "../constants/agentRegistry";
import { useLiveInvestigationStore } from "../store/liveInvestigationStore";

interface CaseContextPanelProps {
  caseId: string;
  selectedAgentId: AgentId;
  onOpenEvidence?: (evidenceId: string) => void;
  onOpenContradictions?: () => void;
  onOpenArchive?: () => void;
  onHandoffToAgent?: (targetAgentId: AgentId) => void;
}

export function CaseContextPanel({
  caseId,
  selectedAgentId,
  onOpenEvidence,
  onOpenContradictions,
  onOpenArchive,
  onHandoffToAgent,
}: CaseContextPanelProps) {
  const { data: workspace, isLoading: wsLoading } = useWorkspace(caseId);
  const { data: progress, isLoading: progLoading } = useWorkspaceProgress(caseId);
  const { data: rawFindings } = useWorkspaceAIFindings(caseId);
  const { findings: liveFindings, contradictions: liveContradictions } = useLiveInvestigationStore();

  const currentAgent = getAgent(selectedAgentId);

  const evidenceCount = workspace?.evidence?.length ?? 0;
  const timelineCount = workspace?.timeline?.length ?? 0;
  const entitiesCount = workspace?.knowledge_graph?.entity_count ?? 0;
  const contradictionsCount = Math.max(liveContradictions.length, workspace?.risk_indicators?.length ?? 0);
  const findingsCount = Math.max(liveFindings.length, rawFindings?.length ?? 0, workspace?.ai_findings?.length ?? 0);

  if (wsLoading || progLoading) {
    return (
      <div className="space-y-4 p-4">
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-28 w-full" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-card/40">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-card/60">
        <div className="flex items-center gap-2">
          <FolderKanban className="h-4 w-4 text-primary" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground">
            Case Context
          </h3>
        </div>
        <Badge variant="outline" className="text-[10px] font-mono">
          {caseId}
        </Badge>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {/* Active Agent Banner */}
          <div className="rounded-lg border bg-background/80 p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">
                Current Agent
              </span>
              <Badge variant="secondary" className="text-[10px] font-mono">
                {currentAgent.category}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary border border-primary/20 shrink-0">
                {(() => {
                  const Icon = currentAgent.icon;
                  return <Icon className="h-4 w-4 stroke-[1.8]" aria-hidden="true" />;
                })()}
              </span>
              <div>
                <h4 className="text-sm font-semibold text-foreground">
                  {currentAgent.name}
                </h4>
                <p className="text-[11px] text-muted-foreground line-clamp-1">
                  {currentAgent.tagline}
                </p>
              </div>
            </div>
          </div>

          {/* Key Shared Context Metrics */}
          <div className="space-y-2">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">
              Shared Investigation Context
            </span>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="rounded border bg-background/60 p-2.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-3.5 w-3.5 text-primary" />
                  <span className="text-muted-foreground">Evidence</span>
                </div>
                <span className="font-bold text-foreground font-mono">{evidenceCount}</span>
              </div>

              <div className="rounded border bg-background/60 p-2.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Brain className="h-3.5 w-3.5 text-indigo-500" />
                  <span className="text-muted-foreground">Findings</span>
                </div>
                <span className="font-bold text-foreground font-mono">{findingsCount}</span>
              </div>

              <div className="rounded border bg-background/60 p-2.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <GitBranch className="h-3.5 w-3.5 text-emerald-500" />
                  <span className="text-muted-foreground">Entities</span>
                </div>
                <span className="font-bold text-foreground font-mono">{entitiesCount}</span>
              </div>

              <div className="rounded border bg-background/60 p-2.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CalendarClock className="h-3.5 w-3.5 text-amber-500" />
                  <span className="text-muted-foreground">Timeline</span>
                </div>
                <span className="font-bold text-foreground font-mono">{timelineCount}</span>
              </div>
            </div>

            <div className="rounded border bg-background/60 p-2.5 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
                <span className="text-muted-foreground">Contradictions</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-amber-600 font-mono">{contradictionsCount}</span>
                {onOpenContradictions && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-5 px-1.5 text-[10px] text-amber-600"
                    onClick={onOpenContradictions}
                  >
                    View Matrix
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Authorized Tools for current agent */}
          <div className="rounded-lg border bg-background/80 p-3 space-y-2">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground flex items-center gap-1.5">
              <Cpu className="h-3 w-3 text-primary" /> Authorized Tools ({currentAgent.tools.length})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {currentAgent.tools.map((tool) => (
                <span
                  key={tool}
                  className="px-2 py-0.5 rounded bg-muted text-[11px] font-mono text-foreground border"
                >
                  {tool}
                </span>
              ))}
            </div>
          </div>

          {/* Quick Handoff Shortcuts */}
          {onHandoffToAgent && (
            <div className="rounded-lg border bg-background/80 p-3 space-y-2">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">
                Recommended Specialist Handoffs
              </span>
              <div className="space-y-1.5">
                {[
                  { id: "timeline" as AgentId, name: "Timeline Agent", desc: "Correlate event sequence" },
                  { id: "geoscope" as AgentId, name: "GeoScope Agent", desc: "Trace location & movement" },
                  { id: "testimony" as AgentId, name: "Testimony Agent", desc: "Cross-check statement alibi" },
                  { id: "report" as AgentId, name: "Report Agent", desc: "Synthesize court-ready report" },
                ]
                  .filter((a) => a.id !== selectedAgentId)
                  .map((target) => {
                    const targetAgentData = getAgent(target.id);
                    const TargetIcon = targetAgentData.icon;
                    return (
                      <button
                        key={target.id}
                        type="button"
                        onClick={() => onHandoffToAgent(target.id)}
                        className="w-full flex items-center justify-between p-2 rounded border bg-card hover:bg-muted/50 text-left transition-colors text-xs"
                      >
                        <div className="flex items-center gap-2">
                          <span className="flex h-6 w-6 items-center justify-center rounded bg-primary/10 text-primary border border-primary/20 shrink-0">
                            <TargetIcon className="h-3.5 w-3.5 stroke-[1.8]" aria-hidden="true" />
                          </span>
                          <div>
                            <div className="font-medium text-foreground">{target.name}</div>
                            <div className="text-[10px] text-muted-foreground">{target.desc}</div>
                          </div>
                        </div>
                        <ArrowRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                      </button>
                    );
                  })}
              </div>
            </div>
          )}

          {/* AI Infrastructure Status Card (Step 9) */}
          <div className="rounded-lg border bg-background/80 p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground flex items-center gap-1">
                <Cpu className="h-3 w-3 text-primary" /> AI Infrastructure
              </span>
              <span className="text-[9px] font-mono text-amber-600 bg-amber-500/10 px-1.5 py-0.2 rounded border border-amber-500/20">
                AUDIT MODE
              </span>
            </div>
            <div className="grid grid-cols-1 gap-1 text-[11px]">
              {[
                { name: "Nebius Token Factory", desc: "Adapter Ready (Live Deferred)", active: false },
                { name: "NVIDIA Nemotron", desc: "4-340B Instruct Reasoning (Deferred)", active: false },
                { name: "Nebius AI Cloud", desc: "Architecture Bridge", active: false },
                { name: "Tavily Web Research", desc: "Tool Bridge (Live API Deferred)", active: false },
                { name: "NemoClaw Sandbox", desc: "CrimeKit Policy Sandbox (Live Deferred)", active: false },
                { name: "OpenShell", desc: "Boundary Enforcement (Live Deferred)", active: false },
                { name: "NeMo Agent Toolkit", desc: "Span Adapter Bridge (Live Deferred)", active: false },
              ].map((item) => (
                <div key={item.name} className="flex items-center justify-between py-0.5">
                  <div className="flex items-center gap-1.5">
                    <span className="text-amber-500 text-xs font-bold">○</span>
                    <span className="font-medium text-foreground">{item.name}</span>
                  </div>
                  <span className="text-[9px] text-muted-foreground font-mono">{item.desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Case Verification & Sealing Status */}
          <div className="rounded-lg border bg-background/80 p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">
                Tamper-Evident Archive
              </span>
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
            </div>
            <p className="text-[11px] text-muted-foreground">
              All findings, tool executions, and sessions are hashed with SHA-256 for court-admissible offline verification.
            </p>
            {onOpenArchive && (
              <Button
                variant="outline"
                size="sm"
                className="w-full text-xs h-7"
                onClick={onOpenArchive}
              >
                Open Case Sealing & Archive
              </Button>
            )}
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
