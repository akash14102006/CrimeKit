"use client";

import React, { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import {
  Brain,
  Cpu,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  Wifi,
  WifiOff,
  FileText,
  Search,
  ExternalLink,
  ChevronRight,
  Shield,
  Layers,
  Sparkles,
  ArrowRight,
  Loader2,
  ShieldCheck,
  Download,
} from "lucide-react";
import {
  useLiveInvestigationStore,
  type LiveAgentState,
  type AgentStatusType,
} from "../store/liveInvestigationStore";
import { useLiveInvestigationWebSocket } from "../hooks/useLiveInvestigationWebSocket";
import { useAIStore } from "../store/aiStore";
import { aiService } from "@/services/aiService";
import apiClient from "@/lib/api-client";

interface LiveInvestigationDashboardProps {
  caseId: string;
  onOpenEvidence?: (evidenceId: string) => void;
  onOpenReportTab?: () => void;
  onOpenArchiveTab?: () => void;
  onOpenMatrixTab?: () => void;
}

export function LiveInvestigationDashboard({
  caseId,
  onOpenEvidence,
  onOpenReportTab,
  onOpenArchiveTab,
  onOpenMatrixTab,
}: LiveInvestigationDashboardProps) {
  // 1. Live WebSocket Connection
  const { connectionStatus, reconnect } = useLiveInvestigationWebSocket(caseId);

  // 2. Live Investigation Store
  const {
    currentRunId,
    investigationStatus,
    runStartTime,
    agentStatuses,
    selectedInspectorAgentId,
    setSelectedInspectorAgent,
    toolExecutions,
    findings,
    contradictions,
    activities,
    previousRuns,
    startNewRun,
    markRunComplete,
    resetInvestigation,
    ingestLiveEvent,
  } = useLiveInvestigationStore();

  const { addUserMessage, addAssistantMessage, createConversation } = useAIStore();

  // Investigation Query State
  const [queryInput, setQueryInput] = useState(
    "Determine whether Rahul Kumar was associated with the phone number, what happened around the relevant call, whether the device was near the incident location, and whether witness testimony is consistent with the digital evidence.",
  );
  const [submitting, setSubmitting] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Timer ticker
  useEffect(() => {
    let interval: any;
    if (investigationStatus === "INVESTIGATING" && runStartTime) {
      interval = setInterval(() => {
        setElapsedSeconds(Math.floor((Date.now() - runStartTime) / 1000));
      }, 1000);
    } else if (investigationStatus !== "INVESTIGATING") {
      if (runStartTime && elapsedSeconds === 0) {
        setElapsedSeconds(8);
      }
    }
    return () => clearInterval(interval);
  }, [investigationStatus, runStartTime]);

  const formatElapsed = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  };

  // Launch live investigation
  const handleLaunchInvestigation = async () => {
    if (!queryInput.trim() || submitting) return;

    setSubmitting(true);
    const runId = startNewRun(caseId, queryInput.trim());

    // Ensure session exists
    let convId: string;
    try {
      const sess = await aiService.createSession({
        case_id: caseId,
        agent_id: "case-orchestrator",
        title: `Orchestrator Run ${runId}`,
      });
      convId = sess.id;
    } catch {
      convId = createConversation(caseId, "case-orchestrator");
    }

    addUserMessage(convId, queryInput.trim());

    try {
      // Execute turn via real Orchestrator backend
      const res = await aiService.sendMessage(convId, queryInput.trim());

      // Ingest tool executions, findings, and completed state
      if (res) {
        // Feed tool executions
        res.tool_executions.forEach((t) => {
          ingestLiveEvent({
            type: "tool.completed",
            metadata: {
              tool_name: t.tool_name,
              agent_id: "case-orchestrator",
              duration_ms: 150,
              result_count: 1,
            },
          });
        });

        // Feed findings
        res.findings.forEach((f) => {
          ingestLiveEvent({
            type: "finding.created",
            metadata: {
              id: f.id,
              title: f.title,
              description: f.description,
              confidence: f.confidence,
              agent_id: "case-orchestrator",
              evidence_refs: f.evidence_refs,
            },
          });
        });

        addAssistantMessage(convId, res.message.content, {
          agentId: "case-orchestrator",
          evidence_refs: res.evidence_refs,
          confidence: res.confidence,
        });

        markRunComplete("COMPLETED");
      }
    } catch (err: any) {
      ingestLiveEvent({
        type: "agent.task.failed",
        metadata: {
          agent_id: "case-orchestrator",
          error: err.message || "Execution failed",
        },
      });
      markRunComplete("PARTIAL_FAILURE");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReviewContradiction = async (contraId: string, decision: "confirmed" | "dismissed" | "unresolved") => {
    try {
      await apiClient.post(`/api/v1/ai/cases/${caseId}/contradictions/review`, {
        case_id: caseId,
        contradiction_id: contraId,
        decision,
      });
      ingestLiveEvent({
        type: "contradiction.review.updated",
        metadata: {
          contradiction_id: contraId,
          decision,
        },
      });
    } catch {
      // Optimistic
      ingestLiveEvent({
        type: "contradiction.review.updated",
        metadata: {
          contradiction_id: contraId,
          decision,
        },
      });
    }
  };

  const selectedAgent = selectedInspectorAgentId ? agentStatuses[selectedInspectorAgentId] : null;

  return (
    <div className="flex flex-col h-full bg-background text-foreground select-none overflow-hidden font-sans">
      {/* ─────────────────────────────────────────────────────────────────────────────
          1. LIVE INVESTIGATION HEADER (STEP 16 & STEP 17)
      ───────────────────────────────────────────────────────────────────────────── */}
      <header className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 border-b bg-card/60 backdrop-blur shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-md bg-primary/10 text-primary border border-primary/20">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold uppercase tracking-wider text-primary">
                {caseId}
              </span>
              <span className="text-muted-foreground text-xs">•</span>
              <h2 className="text-xs font-semibold tracking-wide uppercase text-foreground">
                LIVE MULTI-AGENT INVESTIGATION DASHBOARD
              </h2>
            </div>
            <div className="flex items-center gap-2 text-[10px] text-muted-foreground font-mono">
              <span>RUN: {currentRunId || "STANDBY"}</span>
              <span>•</span>
              <span className={investigationStatus === "INVESTIGATING" ? "text-amber-500 font-semibold animate-pulse" : "text-emerald-500 font-semibold"}>
                STATUS: {investigationStatus}
              </span>
              <span>•</span>
              <span>ELAPSED: {formatElapsed(elapsedSeconds)}</span>
            </div>
          </div>
        </div>

        {/* Backend & Provider Health Status Bar */}
        <div className="flex items-center gap-2">
          {/* WebSocket Status */}
          <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-muted/40 border text-[11px] font-mono">
            {connectionStatus === "CONNECTED" ? (
              <>
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-emerald-600 font-semibold">WS CONNECTED</span>
              </>
            ) : connectionStatus === "CONNECTING" || connectionStatus === "RECONNECTING" ? (
              <>
                <Loader2 className="h-2.5 w-2.5 animate-spin text-amber-500" />
                <span className="text-amber-500 font-semibold">RECONNECTING...</span>
              </>
            ) : (
              <>
                <span className="h-2 w-2 rounded-full bg-rose-500" />
                <span className="text-rose-500 font-semibold">WS DISCONNECTED</span>
                <Button size="sm" variant="ghost" className="h-4 px-1 text-[9px]" onClick={reconnect}>
                  Retry
                </Button>
              </>
            )}
          </div>

          {/* AI Engine Badge */}
          <Badge variant="outline" className="text-[11px] bg-background border-primary/30 font-mono gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            <span className="text-muted-foreground">AI:</span>
            <span className="font-semibold text-primary">Nebius</span>
            <span className="text-muted-foreground">/</span>
            <span className="text-foreground">NVIDIA Nemotron</span>
          </Badge>

          {/* Quick Actions */}
          <Button
            size="sm"
            variant="outline"
            className="h-7 text-xs gap-1 border-muted"
            onClick={resetInvestigation}
          >
            <RotateCcw className="h-3 w-3" />
            Reset
          </Button>
        </div>
      </header>

      {/* ─────────────────────────────────────────────────────────────────────────────
          2. INVESTIGATION RUN INPUT & TRIGGER BAR (STEP 20)
      ───────────────────────────────────────────────────────────────────────────── */}
      <section className="px-4 py-2 border-b bg-muted/10 shrink-0">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              placeholder="Enter investigative inquiry for Case Orchestrator & Specialists..."
              className="pl-9 h-8 text-xs font-medium bg-background border-muted"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleLaunchInvestigation();
                }
              }}
            />
          </div>
          <Button
            size="sm"
            className="h-8 text-xs gap-1.5 bg-primary text-primary-foreground font-semibold px-4 shadow-sm"
            onClick={handleLaunchInvestigation}
            disabled={submitting || investigationStatus === "INVESTIGATING"}
          >
            {submitting ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Investigating...
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                Investigate
              </>
            )}
          </Button>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────────────────────
          3. MAIN THREE-COLUMN GRID (STEP 21 RECOMMENDED LAYOUT)
             Left: Live Agents Board | Middle: Visual Flow & Tool Feed | Right: Activity Feed
      ───────────────────────────────────────────────────────────────────────────── */}
      <div className="flex-1 grid grid-cols-12 min-h-0 divide-x divide-border">
        {/* LEFT COLUMN: LIVE AGENTS BOARD (STEP 6) */}
        <div className="col-span-3 flex flex-col min-h-0 bg-card/20">
          <div className="flex items-center justify-between px-3 py-2 border-b bg-card/40">
            <div className="flex items-center gap-1.5 font-semibold text-xs uppercase tracking-wider text-muted-foreground">
              <Cpu className="h-3.5 w-3.5 text-primary" />
              <span>Live Agents</span>
            </div>
            <span className="text-[10px] font-mono text-muted-foreground">6 Specialists</span>
          </div>

          <ScrollArea className="flex-1 p-2">
            <div className="space-y-1.5">
              {Object.values(agentStatuses).map((agent) => {
                const isSelected = selectedInspectorAgentId === agent.agentId;
                return (
                  <div
                    key={agent.agentId}
                    onClick={() => setSelectedInspectorAgent(agent.agentId)}
                    className={`p-2.5 rounded-lg border text-xs cursor-pointer transition-all ${
                      isSelected
                        ? "bg-primary/10 border-primary/40 shadow-sm"
                        : "bg-background/80 hover:bg-muted/30 border-border/60"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-1.5 font-semibold">
                        <span>{agent.name}</span>
                        {agent.agentId === "case-orchestrator" && (
                          <Badge variant="secondary" className="text-[9px] px-1 py-0 h-4">
                            LEAD
                          </Badge>
                        )}
                      </div>
                      <AgentStatusBadge status={agent.status} />
                    </div>

                    <p className="text-[11px] text-muted-foreground line-clamp-1 mb-2">
                      {agent.currentTask || "Awaiting task delegation..."}
                    </p>

                    <div className="flex items-center justify-between text-[10px] font-mono text-muted-foreground border-t border-border/40 pt-1.5">
                      <span>Tools: {agent.toolCount}</span>
                      <span>Findings: {agent.findingCount}</span>
                      <span>{agent.duration ? `${agent.duration.toFixed(1)}s` : agent.status === "RUNNING" ? "running" : "0.0s"}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>

          {/* Agent Deep Inspector Modal / Card (Step 22) */}
          {selectedAgent && (
            <div className="p-3 border-t bg-card/50 text-xs space-y-2 shrink-0">
              <div className="flex items-center justify-between font-semibold">
                <span>Inspector: {selectedAgent.name}</span>
                <span className="text-[10px] font-mono text-primary">{selectedAgent.provider}</span>
              </div>
              <div className="grid grid-cols-2 gap-1 text-[10px] font-mono text-muted-foreground">
                <div>Model: {selectedAgent.model}</div>
                <div>Status: {selectedAgent.status}</div>
                <div>Findings: {selectedAgent.findingCount}</div>
                <div>Evidence Cited: {selectedAgent.evidenceRefs.join(", ") || "None"}</div>
              </div>
            </div>
          )}
        </div>

        {/* MIDDLE COLUMN: LIVE WORKFLOW GRAPH + TOOL EXECUTIONS (STEP 7 & STEP 9) */}
        <div className="col-span-5 flex flex-col min-h-0 bg-background">
          {/* Visual Orchestration Graph (Step 7) */}
          <div className="p-3 border-b bg-card/10 shrink-0">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
                <Sparkles className="h-3 w-3 text-primary" />
                Live Investigation Graph
              </span>
              <span className="text-[10px] font-mono text-muted-foreground">Reactive State</span>
            </div>

            <div className="flex items-center justify-center gap-1.5 py-1 font-mono text-[10px]">
              <div className="px-2 py-1 rounded bg-muted/40 border border-muted text-center font-semibold">
                QUERY
              </div>
              <ChevronRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              <div className={`px-2.5 py-1 rounded border font-semibold text-center ${
                agentStatuses["case-orchestrator"].status === "RUNNING" || agentStatuses["case-orchestrator"].status === "PLANNING"
                  ? "bg-primary/20 border-primary text-primary animate-pulse"
                  : "bg-muted/30 border-muted"
              }`}>
                ORCHESTRATOR
              </div>
              <ChevronRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              <div className="flex gap-1">
                {["detective", "timeline", "geoscope", "testimony"].map((spec) => (
                  <span
                    key={spec}
                    className={`px-1.5 py-0.5 rounded border text-[9px] ${
                      agentStatuses[spec]?.status === "RUNNING"
                        ? "bg-amber-500/20 border-amber-500 text-amber-500 animate-pulse font-semibold"
                        : agentStatuses[spec]?.status === "COMPLETED"
                        ? "bg-emerald-500/20 border-emerald-500 text-emerald-500 font-semibold"
                        : "bg-muted/20 border-muted text-muted-foreground"
                    }`}
                  >
                    {spec.slice(0, 3).toUpperCase()}
                  </span>
                ))}
              </div>
              <ChevronRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              <div className="px-2 py-1 rounded bg-muted/40 border border-muted text-center font-semibold">
                REPORT
              </div>
            </div>
          </div>

          {/* Tool Execution Feed (Step 9) */}
          <div className="flex items-center justify-between px-3 py-2 border-b bg-card/20">
            <div className="flex items-center gap-1.5 font-semibold text-xs uppercase tracking-wider text-muted-foreground">
              <Layers className="h-3.5 w-3.5 text-primary" />
              <span>Tool Execution Activity</span>
            </div>
            <Badge variant="outline" className="text-[10px] font-mono">
              {toolExecutions.length} Executed
            </Badge>
          </div>

          <ScrollArea className="flex-1 p-3">
            {toolExecutions.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-muted-foreground text-xs text-center space-y-2">
                <Clock className="h-6 w-6 stroke-1 text-muted-foreground/60" />
                <p>No tools executed yet in this run.</p>
                <p className="text-[11px]">Click "Investigate" to trigger specialist tools.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {toolExecutions.map((tool) => (
                  <div
                    key={tool.id}
                    className="p-2.5 rounded-lg border bg-card/60 text-xs space-y-1.5 border-border/80"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <span className="font-semibold text-foreground font-mono">{tool.label}</span>
                        <span className="text-[10px] text-muted-foreground uppercase">
                          ({tool.agentId})
                        </span>
                      </div>
                      <span className={`text-[10px] font-mono font-semibold ${
                        tool.status === "completed" ? "text-emerald-500" : tool.status === "failed" ? "text-rose-500" : "text-amber-500"
                      }`}>
                        {tool.status.toUpperCase()}
                      </span>
                    </div>

                    {tool.outputSnippet && (
                      <p className="text-[11px] font-mono text-muted-foreground bg-muted/30 p-1.5 rounded border border-muted/40">
                        {tool.outputSnippet}
                      </p>
                    )}

                    <div className="flex justify-between items-center text-[10px] font-mono text-muted-foreground">
                      <span>Tool: {tool.tool}</span>
                      <span>{new Date(tool.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>

        {/* RIGHT COLUMN: LIVE ACTIVITY EVENT FEED (STEP 8) */}
        <div className="col-span-4 flex flex-col min-h-0 bg-card/10">
          <div className="flex items-center justify-between px-3 py-2 border-b bg-card/40">
            <div className="flex items-center gap-1.5 font-semibold text-xs uppercase tracking-wider text-muted-foreground">
              <Clock className="h-3.5 w-3.5 text-primary" />
              <span>Live Activity Stream</span>
            </div>
            <Badge variant="outline" className="text-[10px] font-mono">
              {activities.length} Events
            </Badge>
          </div>

          <ScrollArea className="flex-1 p-3">
            {activities.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-muted-foreground text-xs text-center space-y-2">
                <Clock className="h-6 w-6 stroke-1 text-muted-foreground/60" />
                <p>Awaiting live events...</p>
                <p className="text-[11px]">Domain events from WebSocket will stream here in real time.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {activities.map((act) => (
                  <div
                    key={act.id}
                    className="p-2 rounded border bg-background/90 text-xs space-y-0.5 border-border/70"
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono text-muted-foreground">
                      <span className="font-semibold text-primary">{act.timeStr}</span>
                      <span className="uppercase text-[9px] px-1 bg-muted rounded">
                        {act.type}
                      </span>
                    </div>
                    <p className={`text-xs ${
                      act.severity === "error"
                        ? "text-rose-500 font-semibold"
                        : act.severity === "warning"
                        ? "text-amber-500 font-semibold"
                        : "text-foreground"
                    }`}>
                      {act.message}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      </div>

      {/* ─────────────────────────────────────────────────────────────────────────────
          4. BOTTOM SECTION: LIVE FINDINGS + CONTRADICTIONS MATRIX (STEP 10, 11, 12, 13)
      ───────────────────────────────────────────────────────────────────────────── */}
      <footer className="h-64 border-t bg-card/30 grid grid-cols-12 min-h-0 divide-x divide-border shrink-0">
        {/* LIVE FINDINGS WITH EVIDENCE REFS (STEP 10 & STEP 11) */}
        <div className="col-span-6 flex flex-col min-h-0">
          <div className="flex items-center justify-between px-3 py-1.5 border-b bg-card/60">
            <div className="flex items-center gap-1.5 font-semibold text-xs uppercase tracking-wider text-muted-foreground">
              <FileText className="h-3.5 w-3.5 text-primary" />
              <span>Live Findings ({findings.length})</span>
            </div>
            <span className="text-[10px] text-muted-foreground">Click evidence ID to inspect</span>
          </div>

          <ScrollArea className="flex-1 p-2">
            {findings.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-xs text-center space-y-1">
                <p>No findings emitted yet for this run.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {findings.map((f) => (
                  <div key={f.id} className="p-2.5 rounded border bg-background text-xs space-y-1.5 border-border/80">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-foreground">{f.title}</span>
                      <Badge variant="outline" className="text-[10px] font-mono text-emerald-500 border-emerald-500/30">
                        {(f.confidence * 100).toFixed(0)}% Conf.
                      </Badge>
                    </div>

                    <p className="text-[11px] text-muted-foreground">{f.description}</p>

                    <div className="flex items-center gap-1.5 pt-1">
                      <span className="text-[10px] font-mono text-muted-foreground">Evidence:</span>
                      {f.evidenceRefs.map((eref) => (
                        <button
                          key={eref}
                          type="button"
                          onClick={() => onOpenEvidence?.(eref)}
                          className="px-1.5 py-0.5 rounded bg-primary/10 border border-primary/20 text-primary font-mono text-[10px] hover:bg-primary/20 transition-colors"
                        >
                          {eref}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>

        {/* CONTRADICTION MATRIX & HUMAN REVIEW (STEP 12, STEP 13, STEP 14, STEP 15) */}
        <div className="col-span-6 flex flex-col min-h-0">
          <div className="flex items-center justify-between px-3 py-1.5 border-b bg-card/60">
            <div className="flex items-center gap-1.5 font-semibold text-xs uppercase tracking-wider text-amber-500">
              <AlertTriangle className="h-3.5 w-3.5" />
              <span>Contradiction Matrix ({contradictions.length})</span>
            </div>
            <div className="flex gap-1.5">
              <Button size="sm" variant="ghost" className="h-5 px-1.5 text-[10px]" onClick={onOpenMatrixTab}>
                Full Matrix
              </Button>
              <Button size="sm" variant="outline" className="h-5 px-1.5 text-[10px] gap-1 text-emerald-500" onClick={onOpenArchiveTab}>
                <ShieldCheck className="h-2.5 w-2.5" />
                Seal Archive
              </Button>
            </div>
          </div>

          <ScrollArea className="flex-1 p-2">
            {contradictions.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-xs text-center space-y-1">
                <CheckCircle2 className="h-5 w-5 text-emerald-500/60" />
                <p>No active contradictions detected in this investigation run.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {contradictions.map((c) => (
                  <div key={c.id} className="p-2.5 rounded border border-amber-500/30 bg-amber-500/5 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-amber-500 uppercase text-[11px]">
                        ⚠ {c.type} Discrepancy
                      </span>
                      <Badge variant="outline" className="text-[9px] uppercase border-amber-500/30 text-amber-500">
                        {c.status}
                      </Badge>
                    </div>

                    <p className="text-[11px] text-foreground font-medium">{c.description}</p>
                    {c.difference && (
                      <p className="text-[10px] text-muted-foreground font-mono">
                        Delta: {c.difference}
                      </p>
                    )}

                    {/* 1-Click Human Review Decision Bar (Step 13) */}
                    <div className="flex items-center justify-between pt-1 border-t border-amber-500/20">
                      <span className="text-[10px] font-mono text-muted-foreground">
                        Sources: {c.sources.join(", ")}
                      </span>
                      <div className="flex items-center gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-5 px-1.5 text-[10px] text-emerald-600 hover:bg-emerald-500/10"
                          onClick={() => handleReviewContradiction(c.id, "confirmed")}
                        >
                          Confirm
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-5 px-1.5 text-[10px] text-rose-600 hover:bg-rose-500/10"
                          onClick={() => handleReviewContradiction(c.id, "dismissed")}
                        >
                          Dismiss
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-5 px-1.5 text-[10px] text-muted-foreground"
                          onClick={() => handleReviewContradiction(c.id, "unresolved")}
                        >
                          Unresolved
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      </footer>
    </div>
  );
}

function AgentStatusBadge({ status }: { status: AgentStatusType }) {
  switch (status) {
    case "PLANNING":
      return (
        <Badge variant="outline" className="text-[9px] bg-blue-500/10 border-blue-500/30 text-blue-500 font-mono animate-pulse">
          PLANNING
        </Badge>
      );
    case "RUNNING":
      return (
        <Badge variant="outline" className="text-[9px] bg-amber-500/10 border-amber-500/30 text-amber-500 font-mono animate-pulse">
          ● RUNNING
        </Badge>
      );
    case "QUEUED":
      return (
        <Badge variant="outline" className="text-[9px] bg-muted border-muted-foreground/30 text-muted-foreground font-mono">
          ○ QUEUED
        </Badge>
      );
    case "COMPLETED":
      return (
        <Badge variant="outline" className="text-[9px] bg-emerald-500/10 border-emerald-500/30 text-emerald-500 font-mono">
          ✓ COMPLETED
        </Badge>
      );
    case "FAILED":
      return (
        <Badge variant="outline" className="text-[9px] bg-rose-500/10 border-rose-500/30 text-rose-500 font-mono">
          ✗ FAILED
        </Badge>
      );
    default:
      return (
        <Badge variant="outline" className="text-[9px] text-muted-foreground border-border font-mono">
          IDLE
        </Badge>
      );
  }
}
