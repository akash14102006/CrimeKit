import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AgentId } from "../constants/agentRegistry";

export type ToolExecutionStatus = "pending" | "running" | "completed" | "failed";

export interface ToolExecution {
  id: string;
  tool: string;
  label: string;
  status: ToolExecutionStatus;
  timestamp?: number;
  outputSnippet?: string;
}

export interface AgentHandoff {
  targetAgentId: AgentId;
  reason: string;
  contextSummary?: string;
}

export interface AIFinding {
  id: string;
  title: string;
  description: string;
  confidence: number;
  evidenceRefs: string[];
  agentId: AgentId;
  status: "verified" | "needs-review" | "inconclusive";
  subgraphNodes?: string[];
}

export interface AIMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  agentId?: AgentId;
  citations?: AICitation[];
  evidence_refs?: string[];
  kg_refs?: string[];
  timeline_refs?: string[];
  confidence?: number;
  toolExecutions?: ToolExecution[];
  findings?: AIFinding[];
  handoff?: AgentHandoff;
}

export interface AICitation {
  id: string;
  type: "evidence" | "timeline" | "kg" | "processing" | "report";
  label: string;
  source_id?: string;
  confidence?: number;
}

export interface AIConversation {
  id: string;
  title: string;
  case_id?: string;
  agent_id?: AgentId;
  messages: AIMessage[];
  created_at: number;
  updated_at: number;
  pinned: boolean;
}

interface AIWorkspaceState {
  conversations: AIConversation[];
  activeConversationId: string | null;
  selectedAgentId: AgentId;
  isStreaming: boolean;
  streamingMessageId: string | null;
  sidebarOpen: boolean;
  activeTab: "chat" | "findings" | "agents" | "summary" | "correlations";

  setSelectedAgentId: (agentId: AgentId) => void;
  createConversation: (caseId?: string, agentId?: AgentId) => string;
  setActiveConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, title: string) => void;
  togglePinConversation: (id: string) => void;

  addUserMessage: (conversationId: string, content: string) => string;
  addAssistantMessage: (
    conversationId: string,
    content: string,
    meta?: Partial<Pick<AIMessage, "agentId" | "citations" | "evidence_refs" | "kg_refs" | "timeline_refs" | "confidence" | "toolExecutions" | "findings" | "handoff">>,
  ) => string;
  updateMessage: (conversationId: string, messageId: string, content: string) => void;

  setStreaming: (streaming: boolean, messageId?: string | null) => void;
  setSidebarOpen: (open: boolean) => void;
  setActiveTab: (tab: AIWorkspaceState["activeTab"]) => void;

  // Backend session synchronization
  syncSessions: (backendSessions: Array<{ id: string; title: string; case_id: string; agent_id: string; updated_at?: string; pinned?: boolean }>) => void;
  syncMessages: (conversationId: string, messages: AIMessage[]) => void;
}

let _nextId = 1;
function uid(): string {
  return `${Date.now()}-${_nextId++}`;
}

export const useAIStore = create<AIWorkspaceState>()(
  persist(
    (set, get) => ({
      conversations: [],
      activeConversationId: null,
      selectedAgentId: "detective",
      isStreaming: false,
      streamingMessageId: null,
      sidebarOpen: true,
      activeTab: "chat",

      setSelectedAgentId: (agentId) => set({ selectedAgentId: agentId }),

      createConversation: (caseId?: string, agentId?: AgentId) => {
        const id = uid();
        const now = Date.now();
        const activeAgent = agentId || get().selectedAgentId || "detective";
        const conv: AIConversation = {
          id,
          title: `${activeAgent.charAt(0).toUpperCase() + activeAgent.slice(1)} Session ${new Date(now).toLocaleDateString([], { month: "short", day: "numeric" })}`,
          case_id: caseId,
          agent_id: activeAgent,
          messages: [],
          created_at: now,
          updated_at: now,
          pinned: false,
        };
        set((s) => ({
          conversations: [conv, ...s.conversations],
          activeConversationId: id,
          selectedAgentId: activeAgent,
        }));
        return id;
      },

      setActiveConversation: (id) => set({ activeConversationId: id }),

      deleteConversation: (id) =>
        set((s) => ({
          conversations: s.conversations.filter((c) => c.id !== id),
          activeConversationId:
            s.activeConversationId === id ? null : s.activeConversationId,
        })),

      renameConversation: (id, title) =>
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === id ? { ...c, title, updated_at: Date.now() } : c,
          ),
        })),

      togglePinConversation: (id) =>
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === id ? { ...c, pinned: !c.pinned } : c,
          ),
        })),

      addUserMessage: (conversationId, content) => {
        const msgId = uid();
        const msg: AIMessage = {
          id: msgId,
          role: "user",
          content,
          timestamp: Date.now(),
        };
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === conversationId
              ? { ...c, messages: [...c.messages, msg], updated_at: Date.now() }
              : c,
          ),
        }));
        return msgId;
      },

      addAssistantMessage: (conversationId, content, meta) => {
        const msgId = uid();
        const msg: AIMessage = {
          id: msgId,
          role: "assistant",
          content,
          timestamp: Date.now(),
          ...meta,
        };
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === conversationId
              ? { ...c, messages: [...c.messages, msg], updated_at: Date.now() }
              : c,
          ),
        }));
        return msgId;
      },

      updateMessage: (conversationId, messageId, content) =>
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === conversationId
              ? {
                  ...c,
                  messages: c.messages.map((m) =>
                    m.id === messageId ? { ...m, content } : m,
                  ),
                }
              : c,
          ),
        })),

      setStreaming: (streaming, messageId = null) =>
        set({ isStreaming: streaming, streamingMessageId: messageId }),

      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setActiveTab: (tab) => set({ activeTab: tab }),

      syncSessions: (backendSessions) => {
        set((s) => {
          const existingMap = new Map(s.conversations.map((c) => [c.id, c]));
          const merged: AIConversation[] = backendSessions.map((bs) => {
            const existing = existingMap.get(bs.id);
            const ts = bs.updated_at ? new Date(bs.updated_at).getTime() : Date.now();
            if (existing) {
              return {
                ...existing,
                title: bs.title || existing.title,
                agent_id: (bs.agent_id as AgentId) || existing.agent_id,
                case_id: bs.case_id || existing.case_id,
                pinned: bs.pinned ?? existing.pinned,
                updated_at: Math.max(existing.updated_at, ts),
              };
            }
            return {
              id: bs.id,
              title: bs.title,
              case_id: bs.case_id,
              agent_id: bs.agent_id as AgentId,
              messages: [],
              created_at: ts,
              updated_at: ts,
              pinned: bs.pinned ?? false,
            };
          });

          // Retain local conversations that haven't synced yet
          for (const c of s.conversations) {
            if (!backendSessions.some((bs) => bs.id === c.id)) {
              merged.push(c);
            }
          }

          return { conversations: merged };
        });
      },

      syncMessages: (conversationId, messages) => {
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === conversationId ? { ...c, messages } : c,
          ),
        }));
      },
    }),
    {
      name: "crimekit-ai-workspace",
      partialize: (state) => ({
        conversations: state.conversations.slice(0, 50),
        activeConversationId: state.activeConversationId,
        selectedAgentId: state.selectedAgentId,
        sidebarOpen: state.sidebarOpen,
        activeTab: state.activeTab,
      }),
    },
  ),
);
