import { create } from "zustand";
import type { AgentId } from "../constants/agentRegistry";

export type AgentStatusType =
  | "IDLE"
  | "PLANNING"
  | "QUEUED"
  | "RUNNING"
  | "WAITING"
  | "COMPLETED"
  | "FAILED"
  | "SKIPPED";

export interface LiveAgentState {
  agentId: AgentId;
  name: string;
  status: AgentStatusType;
  currentTask?: string;
  provider: string;
  model: string;
  startedAt?: number;
  completedAt?: number;
  duration?: number;
  error?: string;
  findingCount: number;
  toolCount: number;
  evidenceRefs: string[];
}

export interface LiveToolExecution {
  id: string;
  tool: string;
  label: string;
  agentId: string;
  status: "pending" | "running" | "completed" | "failed";
  timestamp: number;
  durationMs?: number;
  outputSnippet?: string;
}

export interface LiveFinding {
  id: string;
  title: string;
  description: string;
  confidence: number;
  evidenceRefs: string[];
  agentId: string;
  status: "verified" | "needs-review" | "inconclusive";
  timestamp: number;
}

export interface LiveContradiction {
  id: string;
  type: string;
  description: string;
  difference?: string;
  status: string;
  sources: string[];
  timestamp: number;
}

export interface LiveActivityEvent {
  id: string;
  timestamp: number;
  timeStr: string;
  type: string;
  agentId?: string;
  message: string;
  severity?: "info" | "success" | "warning" | "error";
  details?: any;
}

export interface LiveInvestigationRun {
  runId: string;
  caseId: string;
  query: string;
  status: "IDLE" | "INVESTIGATING" | "COMPLETED" | "PARTIAL_FAILURE" | "FAILED";
  startedAt: number;
  completedAt?: number;
  findingsCount: number;
  contradictionsCount: number;
  agentsInvolved: string[];
}

export type ConnectionStatus = "DISCONNECTED" | "CONNECTING" | "CONNECTED" | "RECONNECTING" | "ERROR";

interface LiveInvestigationStore {
  // Connection state
  connectionStatus: ConnectionStatus;
  reconnectAttempts: number;
  lastConnectedTime: number | null;
  setConnectionStatus: (status: ConnectionStatus) => void;

  // Active run state
  currentRunId: string | null;
  activeCaseId: string | null;
  investigationStatus: "IDLE" | "PLANNING" | "INVESTIGATING" | "COMPLETED" | "PARTIAL_FAILURE" | "FAILED";
  runStartTime: number | null;
  runEndTime: number | null;

  // Previous runs history
  previousRuns: LiveInvestigationRun[];

  // Live agents state
  agentStatuses: Record<string, LiveAgentState>;
  selectedInspectorAgentId: string | null;
  setSelectedInspectorAgent: (agentId: string | null) => void;

  // Live data feeds
  toolExecutions: LiveToolExecution[];
  findings: LiveFinding[];
  contradictions: LiveContradiction[];
  activities: LiveActivityEvent[];

  // Processed event tracking for deduplication
  processedEventIds: Set<string>;

  // Actions
  startNewRun: (caseId: string, query: string, customRunId?: string) => string;
  markRunComplete: (status?: "COMPLETED" | "PARTIAL_FAILURE" | "FAILED") => void;
  resetInvestigation: () => void;

  // Event ingestion
  ingestLiveEvent: (event: any) => void;
}

const INITIAL_AGENTS: Record<string, LiveAgentState> = {
  "case-orchestrator": {
    agentId: "case-orchestrator",
    name: "Case Orchestrator",
    status: "IDLE",
    provider: "Nebius",
    model: "NVIDIA Nemotron (Orchestrator)",
    findingCount: 0,
    toolCount: 0,
    evidenceRefs: [],
  },
  detective: {
    agentId: "detective",
    name: "Detective",
    status: "IDLE",
    provider: "Nebius",
    model: "NVIDIA Nemotron",
    findingCount: 0,
    toolCount: 0,
    evidenceRefs: [],
  },
  timeline: {
    agentId: "timeline",
    name: "Timeline",
    status: "IDLE",
    provider: "Nebius",
    model: "NVIDIA Nemotron",
    findingCount: 0,
    toolCount: 0,
    evidenceRefs: [],
  },
  geoscope: {
    agentId: "geoscope",
    name: "GeoScope",
    status: "IDLE",
    provider: "Nebius",
    model: "NVIDIA Nemotron",
    findingCount: 0,
    toolCount: 0,
    evidenceRefs: [],
  },
  testimony: {
    agentId: "testimony",
    name: "Testimony",
    status: "IDLE",
    provider: "Nebius",
    model: "NVIDIA Nemotron",
    findingCount: 0,
    toolCount: 0,
    evidenceRefs: [],
  },
  report: {
    agentId: "report",
    name: "Report",
    status: "IDLE",
    provider: "Nebius",
    model: "NVIDIA Nemotron",
    findingCount: 0,
    toolCount: 0,
    evidenceRefs: [],
  },
};

function formatTime(timestamp: number): string {
  const d = new Date(timestamp);
  return d.toTimeString().split(" ")[0];
}

export const useLiveInvestigationStore = create<LiveInvestigationStore>((set, get) => ({
  connectionStatus: "DISCONNECTED",
  reconnectAttempts: 0,
  lastConnectedTime: null,
  setConnectionStatus: (status) =>
    set({
      connectionStatus: status,
      lastConnectedTime: status === "CONNECTED" ? Date.now() : get().lastConnectedTime,
      reconnectAttempts: status === "CONNECTED" ? 0 : get().reconnectAttempts,
    }),

  currentRunId: null,
  activeCaseId: null,
  investigationStatus: "IDLE",
  runStartTime: null,
  runEndTime: null,

  previousRuns: [],
  agentStatuses: { ...INITIAL_AGENTS },
  selectedInspectorAgentId: null,
  setSelectedInspectorAgent: (agentId) => set({ selectedInspectorAgentId: agentId }),

  toolExecutions: [],
  findings: [],
  contradictions: [],
  activities: [],
  processedEventIds: new Set<string>(),

  startNewRun: (caseId: string, query: string, customRunId?: string) => {
    const now = Date.now();
    const runNumber = get().previousRuns.length + 1;
    const runId = customRunId || `INV-${caseId.slice(-4).toUpperCase()}-${String(runNumber).padStart(3, "0")}`;

    // Reset agent state for fresh run
    const resetAgents = Object.keys(INITIAL_AGENTS).reduce((acc, id) => {
      acc[id] = {
        ...INITIAL_AGENTS[id],
        status: id === "case-orchestrator" ? "PLANNING" : "IDLE",
        startedAt: id === "case-orchestrator" ? now : undefined,
      };
      return acc;
    }, {} as Record<string, LiveAgentState>);

    const initialActivity: LiveActivityEvent = {
      id: `act-${now}-init`,
      timestamp: now,
      timeStr: formatTime(now),
      type: "orchestration.started",
      agentId: "case-orchestrator",
      message: `Investigation started: "${query.slice(0, 60)}${query.length > 60 ? "..." : ""}"`,
      severity: "info",
    };

    set({
      currentRunId: runId,
      activeCaseId: caseId,
      investigationStatus: "INVESTIGATING",
      runStartTime: now,
      runEndTime: null,
      agentStatuses: resetAgents,
      toolExecutions: [],
      findings: [],
      contradictions: [],
      activities: [initialActivity],
      selectedInspectorAgentId: "case-orchestrator",
    });

    return runId;
  },

  markRunComplete: (finalStatus = "COMPLETED") => {
    const state = get();
    if (!state.currentRunId || !state.activeCaseId) return;

    const completedRun: LiveInvestigationRun = {
      runId: state.currentRunId,
      caseId: state.activeCaseId,
      query: state.activities[0]?.message || "Multi-agent investigation",
      status: finalStatus,
      startedAt: state.runStartTime || Date.now(),
      completedAt: Date.now(),
      findingsCount: state.findings.length,
      contradictionsCount: state.contradictions.length,
      agentsInvolved: Object.keys(state.agentStatuses).filter(
        (id) => state.agentStatuses[id].status === "COMPLETED" || state.agentStatuses[id].status === "RUNNING",
      ),
    };

    set((s) => ({
      investigationStatus: finalStatus,
      runEndTime: Date.now(),
      previousRuns: [completedRun, ...s.previousRuns.slice(0, 9)],
    }));
  },

  resetInvestigation: () => {
    set({
      investigationStatus: "IDLE",
      currentRunId: null,
      runStartTime: null,
      runEndTime: null,
      agentStatuses: { ...INITIAL_AGENTS },
      toolExecutions: [],
      findings: [],
      contradictions: [],
      activities: [],
      selectedInspectorAgentId: null,
    });
  },

  ingestLiveEvent: (rawEvent: any) => {
    if (!rawEvent) return;

    // Normalization
    const eventType = rawEvent.type || rawEvent.event || rawEvent.event_type || "";
    const eventId = rawEvent.event_id || rawEvent.id || `${eventType}-${rawEvent.timestamp || Date.now()}-${JSON.stringify(rawEvent.metadata || rawEvent.payload || {}).slice(0, 30)}`;
    const metadata = rawEvent.metadata || rawEvent.payload || rawEvent;
    const now = Date.now();
    const eventTime = rawEvent.timestamp ? (typeof rawEvent.timestamp === "number" && rawEvent.timestamp < 10000000000 ? rawEvent.timestamp * 1000 : Number(rawEvent.timestamp) || now) : now;

    // Deduplication check
    const processed = get().processedEventIds;
    if (processed.has(eventId)) {
      return;
    }
    processed.add(eventId);

    const timeStr = formatTime(eventTime);

    // 1. ORCHESTRATION EVENTS
    if (eventType === "orchestration.started") {
      set((s) => ({
        investigationStatus: "INVESTIGATING",
        agentStatuses: {
          ...s.agentStatuses,
          "case-orchestrator": {
            ...s.agentStatuses["case-orchestrator"],
            status: "PLANNING",
            startedAt: eventTime,
            currentTask: metadata.query || "Evaluating investigation objective and specialist routing",
          },
        },
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId: "case-orchestrator",
            message: "Case Orchestrator initialized investigation plan",
            severity: "info",
          },
          ...s.activities,
        ],
      }));
    } else if (eventType === "orchestration.delegated") {
      const targetAgent = metadata.target_agent || metadata.agent_id || "detective";
      set((s) => ({
        agentStatuses: {
          ...s.agentStatuses,
          "case-orchestrator": {
            ...s.agentStatuses["case-orchestrator"],
            status: "RUNNING",
            currentTask: `Supervising delegated analysis for ${targetAgent}`,
          },
          [targetAgent]: {
            ...(s.agentStatuses[targetAgent] || {
              agentId: targetAgent as any,
              name: targetAgent.charAt(0).toUpperCase() + targetAgent.slice(1),
              provider: "Nebius",
              model: "NVIDIA Nemotron",
              findingCount: 0,
              toolCount: 0,
              evidenceRefs: [],
            }),
            status: "RUNNING",
            startedAt: eventTime,
            currentTask: metadata.objective || `Analyzing leads for case`,
          },
        },
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId: "case-orchestrator",
            message: `Delegated task → ${targetAgent.charAt(0).toUpperCase() + targetAgent.slice(1)}: "${(metadata.objective || "").slice(0, 60)}"`,
            severity: "info",
          },
          ...s.activities,
        ],
      }));
    } else if (eventType === "orchestration.completed") {
      set((s) => ({
        investigationStatus: "COMPLETED",
        runEndTime: eventTime,
        agentStatuses: {
          ...s.agentStatuses,
          "case-orchestrator": {
            ...s.agentStatuses["case-orchestrator"],
            status: "COMPLETED",
            completedAt: eventTime,
            duration: s.agentStatuses["case-orchestrator"]?.startedAt ? (eventTime - s.agentStatuses["case-orchestrator"].startedAt) / 1000 : 8.5,
          },
        },
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId: "case-orchestrator",
            message: "Case Orchestrator completed investigation synthesis",
            severity: "success",
          },
          ...s.activities,
        ],
      }));
    }

    // 2. AGENT TASK EVENTS
    else if (eventType === "agent.task.started") {
      const agentId = metadata.agent_id || "detective";
      set((s) => ({
        agentStatuses: {
          ...s.agentStatuses,
          [agentId]: {
            ...(s.agentStatuses[agentId] || INITIAL_AGENTS[agentId] || {
              agentId: agentId as any,
              name: agentId,
              provider: "Nebius",
              model: "NVIDIA Nemotron",
              findingCount: 0,
              toolCount: 0,
              evidenceRefs: [],
            }),
            status: "RUNNING",
            startedAt: eventTime,
            currentTask: metadata.description || "Executing assigned task",
          },
        },
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId,
            message: `${agentId.charAt(0).toUpperCase() + agentId.slice(1)} started subtask: "${(metadata.description || "").slice(0, 50)}"`,
            severity: "info",
          },
          ...s.activities,
        ],
      }));
    } else if (eventType === "agent.task.completed") {
      const agentId = metadata.agent_id || "detective";
      set((s) => {
        const curAgent = s.agentStatuses[agentId];
        const started = curAgent?.startedAt || eventTime - 2000;
        const dur = (eventTime - started) / 1000;
        return {
          agentStatuses: {
            ...s.agentStatuses,
            [agentId]: {
              ...curAgent,
              status: "COMPLETED",
              completedAt: eventTime,
              duration: metadata.duration_ms ? metadata.duration_ms / 1000 : dur,
              findingCount: (curAgent?.findingCount || 0) + (metadata.finding_count || 0),
              evidenceRefs: Array.from(new Set([...(curAgent?.evidenceRefs || []), ...(metadata.evidence_refs || [])])),
            },
          },
          activities: [
            {
              id: eventId,
              timestamp: eventTime,
              timeStr,
              type: eventType,
              agentId,
              message: `${agentId.charAt(0).toUpperCase() + agentId.slice(1)} completed task in ${metadata.duration_ms ? (metadata.duration_ms / 1000).toFixed(1) : dur.toFixed(1)}s`,
              severity: "success",
            },
            ...s.activities,
          ],
        };
      });
    } else if (eventType === "agent.task.failed") {
      const agentId = metadata.agent_id || "geoscope";
      set((s) => ({
        investigationStatus: "PARTIAL_FAILURE",
        agentStatuses: {
          ...s.agentStatuses,
          [agentId]: {
            ...(s.agentStatuses[agentId] || INITIAL_AGENTS[agentId]),
            status: "FAILED",
            completedAt: eventTime,
            error: metadata.error || "Specialist execution failed",
          },
        },
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId,
            message: `${agentId.charAt(0).toUpperCase() + agentId.slice(1)} failed: ${metadata.error || "Execution error"}`,
            severity: "error",
          },
          ...s.activities,
        ],
      }));
    }

    // 3. TOOL EVENTS
    else if (eventType === "tool.started") {
      const toolName = metadata.tool_name || metadata.tool || "tool";
      const agentId = metadata.agent_id || "detective";
      const toolId = metadata.tool_id || `tool-${toolName}-${eventTime}`;

      const newTool: LiveToolExecution = {
        id: toolId,
        tool: toolName,
        label: toolName.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
        agentId,
        status: "running",
        timestamp: eventTime,
      };

      set((s) => ({
        toolExecutions: [newTool, ...s.toolExecutions.filter((t) => t.id !== toolId)],
        agentStatuses: {
          ...s.agentStatuses,
          [agentId]: {
            ...s.agentStatuses[agentId],
            toolCount: (s.agentStatuses[agentId]?.toolCount || 0) + 1,
          },
        },
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId,
            message: `${agentId.charAt(0).toUpperCase() + agentId.slice(1)} → ${newTool.label}`,
            severity: "info",
          },
          ...s.activities,
        ],
      }));
    } else if (eventType === "tool.completed") {
      const toolName = metadata.tool_name || metadata.tool || "tool";
      const agentId = metadata.agent_id || "detective";
      set((s) => ({
        toolExecutions: s.toolExecutions.map((t) => {
          if (t.tool === toolName && t.agentId === agentId && t.status === "running") {
            return {
              ...t,
              status: "completed",
              durationMs: metadata.duration_ms || 120,
              outputSnippet: metadata.output_snippet || `Returned ${metadata.result_count ?? "matched"} records.`,
            };
          }
          return t;
        }),
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId,
            message: `Tool completed: ${toolName.replace(/_/g, " ")} (${metadata.result_count !== undefined ? `${metadata.result_count} items` : "success"})`,
            severity: "success",
          },
          ...s.activities,
        ],
      }));
    } else if (eventType === "tool.failed") {
      const toolName = metadata.tool_name || metadata.tool || "tool";
      const agentId = metadata.agent_id || "detective";
      set((s) => ({
        toolExecutions: s.toolExecutions.map((t) => {
          if (t.tool === toolName && t.agentId === agentId && t.status === "running") {
            return {
              ...t,
              status: "failed",
              outputSnippet: metadata.error || "Tool failed.",
            };
          }
          return t;
        }),
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId,
            message: `Tool failed: ${toolName} (${metadata.error || "Unknown error"})`,
            severity: "error",
          },
          ...s.activities,
        ],
      }));
    }

    // 4. FINDING EVENTS
    else if (eventType === "finding.created") {
      const findingId = metadata.id || `find-${now}`;
      const newFinding: LiveFinding = {
        id: findingId,
        title: metadata.title || "Discovered Forensic Finding",
        description: metadata.description || "",
        confidence: metadata.confidence ?? 0.9,
        evidenceRefs: metadata.evidence_refs || [],
        agentId: metadata.agent_id || "detective",
        status: metadata.status === "verified" ? "verified" : metadata.status === "contradicted" ? "inconclusive" : "needs-review",
        timestamp: eventTime,
      };

      set((s) => ({
        findings: [newFinding, ...s.findings.filter((f) => f.id !== findingId)],
        agentStatuses: {
          ...s.agentStatuses,
          [newFinding.agentId]: {
            ...s.agentStatuses[newFinding.agentId],
            findingCount: (s.agentStatuses[newFinding.agentId]?.findingCount || 0) + 1,
            evidenceRefs: Array.from(new Set([...(s.agentStatuses[newFinding.agentId]?.evidenceRefs || []), ...newFinding.evidenceRefs])),
          },
        },
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId: newFinding.agentId,
            message: `New Finding: "${newFinding.title.slice(0, 50)}" [${newFinding.evidenceRefs.join(", ") || "No ref"}]`,
            severity: "success",
          },
          ...s.activities,
        ],
      }));
    }

    // 5. CONTRADICTION EVENTS
    else if (eventType === "contradiction.detected" || eventType === "orchestration.contradiction.detected") {
      const contraId = metadata.contradiction_id || metadata.id || `contra-${now}`;
      const newContra: LiveContradiction = {
        id: contraId,
        type: metadata.type || "temporal",
        description: metadata.description || metadata.statement_excerpt || "Discrepancy detected across evidence sources",
        difference: metadata.difference_description || metadata.difference || undefined,
        status: metadata.status || "needs_review",
        sources: metadata.sources || metadata.evidence_refs || [],
        timestamp: eventTime,
      };

      set((s) => ({
        contradictions: [newContra, ...s.contradictions.filter((c) => c.id !== contraId)],
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            message: `⚠ Contradiction Detected: ${newContra.type.toUpperCase()} conflict identified across ${newContra.sources.join(", ") || "sources"}`,
            severity: "warning",
          },
          ...s.activities,
        ],
      }));
    } else if (eventType === "contradiction.review.updated") {
      const contraId = metadata.contradiction_id;
      set((s) => ({
        contradictions: s.contradictions.map((c) => (c.id === contraId ? { ...c, status: metadata.decision || c.status } : c)),
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            message: `Contradiction ${contraId} marked as ${metadata.decision?.toUpperCase() || "REVIEWED"} by investigator`,
            severity: "info",
          },
          ...s.activities,
        ],
      }));
    }

    // 6. REPORT & ARCHIVE EVENTS
    else if (eventType === "report.generated" || eventType === "report.started") {
      const isStart = eventType === "report.started";
      set((s) => ({
        agentStatuses: {
          ...s.agentStatuses,
          report: {
            ...s.agentStatuses.report,
            status: isStart ? "RUNNING" : "COMPLETED",
            startedAt: isStart ? eventTime : s.agentStatuses.report.startedAt,
            completedAt: !isStart ? eventTime : undefined,
          },
        },
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            agentId: "report",
            message: isStart ? "Report Agent generating forensic case synthesis..." : "Report Agent finalized PDF/JSON investigation report",
            severity: isStart ? "info" : "success",
          },
          ...s.activities,
        ],
      }));
    } else if (eventType === "case.archive.sealed") {
      set((s) => ({
        activities: [
          {
            id: eventId,
            timestamp: eventTime,
            timeStr,
            type: eventType,
            message: `Case sealed! Master Merkle Root: ${String(metadata.root_hash || metadata.case_root_hash || "").slice(0, 16)}...`,
            severity: "success",
          },
          ...s.activities,
        ],
      }));
    }
  },
}));
