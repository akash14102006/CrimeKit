import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AIMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  citations?: AICitation[];
  evidence_refs?: string[];
  kg_refs?: string[];
  timeline_refs?: string[];
  confidence?: number;
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
  messages: AIMessage[];
  created_at: number;
  updated_at: number;
  pinned: boolean;
}

interface AIWorkspaceState {
  conversations: AIConversation[];
  activeConversationId: string | null;
  isStreaming: boolean;
  streamingMessageId: string | null;
  sidebarOpen: boolean;
  activeTab: "chat" | "findings" | "agents" | "summary" | "correlations";

  createConversation: (caseId?: string) => string;
  setActiveConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, title: string) => void;
  togglePinConversation: (id: string) => void;

  addUserMessage: (conversationId: string, content: string) => string;
  addAssistantMessage: (
    conversationId: string,
    content: string,
    meta?: Partial<Pick<AIMessage, "citations" | "evidence_refs" | "kg_refs" | "timeline_refs" | "confidence">>,
  ) => string;
  updateMessage: (conversationId: string, messageId: string, content: string) => void;

  setStreaming: (streaming: boolean, messageId?: string | null) => void;
  setSidebarOpen: (open: boolean) => void;
  setActiveTab: (tab: AIWorkspaceState["activeTab"]) => void;
}

let _nextId = 1;
function uid(): string {
  return `${Date.now()}-${_nextId++}`;
}

export const useAIStore = create<AIWorkspaceState>()(
  persist(
    (set) => ({
      conversations: [],
      activeConversationId: null,
      isStreaming: false,
      streamingMessageId: null,
      sidebarOpen: true,
      activeTab: "chat",

      createConversation: (caseId?: string) => {
        const id = uid();
        const now = Date.now();
        const conv: AIConversation = {
          id,
          title: `Investigation ${new Date(now).toLocaleDateString()}`,
          case_id: caseId,
          messages: [],
          created_at: now,
          updated_at: now,
          pinned: false,
        };
        set((s) => ({
          conversations: [conv, ...s.conversations],
          activeConversationId: id,
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
    }),
    {
      name: "crimekit-ai-workspace",
      partialize: (state) => ({
        conversations: state.conversations.slice(0, 50),
        activeConversationId: state.activeConversationId,
        sidebarOpen: state.sidebarOpen,
        activeTab: state.activeTab,
      }),
    },
  ),
);
