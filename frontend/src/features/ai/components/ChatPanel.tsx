"use client";

import { useCallback, useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { MessageSquare } from "lucide-react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { useAIStore, type AIMessage } from "../store/aiStore";
import { useAIQuery } from "../hooks/useAIWorkspace";

import { getAgent, type AgentId } from "../constants/agentRegistry";
import { generateMockAgentResponse } from "../services/mockAgentResponses";
import { aiService } from "@/services/aiService";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Shield, Wrench } from "lucide-react";

export function ChatPanel({
  caseId,
  onViewEvidence,
}: {
  caseId?: string;
  onViewEvidence?: (evidenceId: string) => void;
}) {
  const {
    conversations,
    activeConversationId,
    selectedAgentId,
    setSelectedAgentId,
    isStreaming,
    addUserMessage,
    addAssistantMessage,
    setStreaming,
    createConversation,
  } = useAIStore();

  const scrollRef = useRef<HTMLDivElement>(null);
  const aiQuery = useAIQuery();
  const currentAgent = getAgent(selectedAgentId);

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId,
  );

  const messages = activeConversation?.messages ?? [];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages.length]);

  const handleAcceptHandoff = useCallback(
    async (targetAgentId: AgentId) => {
      setSelectedAgentId(targetAgentId);
      const targetAgent = getAgent(targetAgentId);
      const continuationPrompt = `Continuation: Investigating lead transferred from ${currentAgent.shortName}...`;

      let convId = activeConversationId;
      if (!convId) {
        convId = createConversation(caseId, targetAgentId);
      }
      addUserMessage(convId, continuationPrompt);
      setStreaming(true);

      // Attempt backend session turn
      try {
        if (caseId) {
          // If conversation ID is UUID, try sending to backend session directly
          let turnResp: import("@/services/aiService").BackendChatTurnResponse | null = null;
          try {
            turnResp = await aiService.sendMessage(convId, continuationPrompt);
          } catch {
            // If session doesn't exist on backend yet, create it and send message
            const newSession = await aiService.createSession({
              case_id: caseId,
              agent_id: targetAgentId,
              title: `${targetAgent.name} Handoff`,
            });
            convId = newSession.id;
            turnResp = await aiService.sendMessage(newSession.id, continuationPrompt);
          }

          if (turnResp) {
            addAssistantMessage(convId!, turnResp.message.content, {
              agentId: targetAgentId,
              toolExecutions: turnResp.tool_executions.map((t) => ({
                id: t.id,
                tool: t.tool_name,
                label: t.display_name,
                status: t.status,
                outputSnippet: t.output_snippet,
              })),
              findings: turnResp.findings.map((f) => ({
                id: f.id,
                title: f.title,
                description: f.description,
                confidence: f.confidence,
                evidenceRefs: f.evidence_refs,
                agentId: targetAgentId,
                status: f.status === "supported" ? "verified" : f.status === "contradicted" ? "inconclusive" : "needs-review",
              })),
              evidence_refs: turnResp.evidence_refs,
              confidence: turnResp.confidence,
              handoff: turnResp.handoff ? {
                targetAgentId: turnResp.handoff.target_agent as AgentId,
                reason: turnResp.handoff.reason,
                contextSummary: turnResp.handoff.context_summary,
              } : undefined,
            });
            setStreaming(false);
            return;
          }
        }
      } catch {
        // Fallback to local mock if backend is unavailable
      }

      // Local fallback
      setTimeout(() => {
        const mockResp = generateMockAgentResponse(
          targetAgentId,
          `Lead transferred from ${currentAgent.shortName}`,
          caseId,
        );
        addAssistantMessage(convId!, mockResp.content, {
          agentId: targetAgentId,
          toolExecutions: mockResp.toolExecutions,
          findings: mockResp.findings,
          citations: mockResp.citations,
          evidence_refs: mockResp.evidence_refs,
          confidence: mockResp.confidence,
          handoff: mockResp.handoff,
        });
        setStreaming(false);
      }, 600);
    },
    [
      activeConversationId,
      caseId,
      currentAgent.shortName,
      setSelectedAgentId,
      createConversation,
      addUserMessage,
      addAssistantMessage,
      setStreaming,
    ],
  );

  const handleHandoffFinding = useCallback(
    async (targetAgentId: AgentId, finding: import("../store/aiStore").AIFinding) => {
      setSelectedAgentId(targetAgentId);
      const targetAgent = getAgent(targetAgentId);
      const evidenceList = finding.evidenceRefs?.join(", ") || "None";
      const handoffPrompt = `Analyze the timeline and context associated with finding: "${finding.title}". Evidence: [${evidenceList}]. Finding details: ${finding.description}`;

      // Switch to existing conversation for this target agent or create one
      const existingConv = conversations.find(
        (c) => c.case_id === caseId && c.agent_id === targetAgentId,
      );
      let convId = existingConv ? existingConv.id : createConversation(caseId, targetAgentId);
      useAIStore.getState().setActiveConversation(convId);

      addUserMessage(convId, handoffPrompt);
      setStreaming(true);

      try {
        if (caseId) {
          let turnResp: import("@/services/aiService").BackendChatTurnResponse | null = null;
          try {
            turnResp = await aiService.sendMessage(convId, handoffPrompt);
          } catch {
            const newSession = await aiService.createSession({
              case_id: caseId,
              agent_id: targetAgentId,
              title: `${targetAgent.shortName}: ${finding.title.slice(0, 30)}`,
            });
            convId = newSession.id;
            useAIStore.getState().setActiveConversation(convId);
            turnResp = await aiService.sendMessage(newSession.id, handoffPrompt);
          }

          if (turnResp) {
            addAssistantMessage(convId, turnResp.message.content, {
              agentId: targetAgentId,
              toolExecutions: turnResp.tool_executions.map((t) => ({
                id: t.id,
                tool: t.tool_name,
                label: t.display_name,
                status: t.status,
                outputSnippet: t.output_snippet,
              })),
              findings: turnResp.findings.map((f) => ({
                id: f.id,
                title: f.title,
                description: f.description,
                confidence: f.confidence,
                evidenceRefs: f.evidence_refs,
                agentId: targetAgentId,
                status: f.status === "supported" ? "verified" : f.status === "contradicted" ? "inconclusive" : "needs-review",
              })),
              evidence_refs: turnResp.evidence_refs,
              confidence: turnResp.confidence,
              handoff: turnResp.handoff ? {
                targetAgentId: turnResp.handoff.target_agent as AgentId,
                reason: turnResp.handoff.reason,
                contextSummary: turnResp.handoff.context_summary,
              } : undefined,
            });
            setStreaming(false);
            return;
          }
        }
      } catch {
        // Fallback to local
      }

      setTimeout(() => {
        const mockResp = generateMockAgentResponse(
          targetAgentId,
          `Investigate finding from ${currentAgent.shortName}: ${finding.title}`,
          caseId,
        );
        addAssistantMessage(convId, mockResp.content, {
          agentId: targetAgentId,
          toolExecutions: mockResp.toolExecutions,
          findings: mockResp.findings,
          citations: mockResp.citations,
          evidence_refs: mockResp.evidence_refs,
          confidence: mockResp.confidence,
          handoff: mockResp.handoff,
        });
        setStreaming(false);
      }, 600);
    },
    [
      caseId,
      conversations,
      currentAgent.shortName,
      setSelectedAgentId,
      createConversation,
      addUserMessage,
      addAssistantMessage,
      setStreaming,
    ],
  );

  const handleSend = useCallback(
    async (content: string) => {
      let convId = activeConversationId;
      if (!convId) {
        convId = createConversation(caseId, selectedAgentId);
      }

      addUserMessage(convId, content);
      setStreaming(true);

      // ── 1. Try Backend Agent Session API (Phase 2) ──
      try {
        if (caseId) {
          let turnResp: import("@/services/aiService").BackendChatTurnResponse | null = null;
          try {
            turnResp = await aiService.sendMessage(convId, content);
          } catch {
            // Lazy session creation on backend if session ID doesn't exist yet
            const newSession = await aiService.createSession({
              case_id: caseId,
              agent_id: selectedAgentId,
              title: content.slice(0, 36),
            });
            convId = newSession.id;
            turnResp = await aiService.sendMessage(newSession.id, content);
          }

          if (turnResp) {
            addAssistantMessage(convId!, turnResp.message.content, {
              agentId: selectedAgentId,
              toolExecutions: turnResp.tool_executions.map((t) => ({
                id: t.id,
                tool: t.tool_name,
                label: t.display_name,
                status: t.status,
                outputSnippet: t.output_snippet,
              })),
              findings: turnResp.findings.map((f) => ({
                id: f.id,
                title: f.title,
                description: f.description,
                confidence: f.confidence,
                evidenceRefs: f.evidence_refs,
                agentId: selectedAgentId,
                status: f.status === "supported" ? "verified" : f.status === "contradicted" ? "inconclusive" : "needs-review",
              })),
              evidence_refs: turnResp.evidence_refs,
              confidence: turnResp.confidence,
              handoff: turnResp.handoff ? {
                targetAgentId: turnResp.handoff.target_agent as AgentId,
                reason: turnResp.handoff.reason,
                contextSummary: turnResp.handoff.context_summary,
              } : undefined,
            });
            setStreaming(false);
            return;
          }
        }
      } catch {
        // Backend session unavailable -> Fallback cleanly to Phase 1 local engine
      }

      // ── 2. Local Fallback Simulation ──
      try {
        let backendHits: Array<{ snippet?: string; text?: string; evidence_id?: string; score: number }> = [];
        try {
          const resp = await aiQuery.mutateAsync({
            query: content,
            case_id: caseId,
            top_k: 5,
          });
          if (resp?.results) backendHits = resp.results;
        } catch {
          // Backend query optional
        }

        setTimeout(() => {
          const mockResp = generateMockAgentResponse(
            selectedAgentId,
            content,
            caseId,
          );

          if (backendHits.length > 0) {
            backendHits.forEach((hit, idx) => {
              if (hit.evidence_id && !mockResp.evidence_refs?.includes(hit.evidence_id)) {
                mockResp.evidence_refs?.push(hit.evidence_id);
                mockResp.citations?.push({
                  id: `backend-cite-${idx}`,
                  type: "evidence",
                  label: `Evidence ${hit.evidence_id.slice(0, 8)}`,
                  source_id: hit.evidence_id,
                  confidence: hit.score,
                });
              }
            });
          }

          addAssistantMessage(convId!, mockResp.content, {
            agentId: selectedAgentId,
            toolExecutions: mockResp.toolExecutions,
            findings: mockResp.findings,
            citations: mockResp.citations,
            evidence_refs: mockResp.evidence_refs,
            confidence: mockResp.confidence,
            handoff: mockResp.handoff,
          });
          setStreaming(false);
        }, 600);
      } catch (error: unknown) {
        const errMsg =
          error instanceof Error ? error.message : "Unknown error occurred";
        addAssistantMessage(
          convId!,
          `Error: Failed to process agent request. ${errMsg}`,
          { confidence: 0, agentId: selectedAgentId },
        );
        setStreaming(false);
      }
    },
    [
      activeConversationId,
      caseId,
      selectedAgentId,
      addUserMessage,
      addAssistantMessage,
      setStreaming,
      createConversation,
      aiQuery,
    ],
  );

  const handleStop = useCallback(() => {
    setStreaming(false);
  }, [setStreaming]);

  return (
    <div className="flex h-full flex-col">
      {/* Agent Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b bg-card/60 backdrop-blur-sm">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0 border border-primary/20">
            {(() => {
              const Icon = currentAgent.icon;
              return <Icon className="h-4 w-4 stroke-[1.8]" aria-hidden="true" />;
            })()}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold truncate text-foreground">
                {currentAgent.name}
              </h2>
              <Badge variant="outline" className="text-[10px] font-mono px-1.5 py-0 h-4 uppercase">
                {currentAgent.category}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground truncate">
              {currentAgent.tagline}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {/* Agent Tools dropdown or badges */}
          <div className="hidden lg:flex items-center gap-1">
            <span className="text-[10px] text-muted-foreground mr-1 flex items-center gap-1">
              <Wrench className="h-2.5 w-2.5" /> Tools:
            </span>
            {currentAgent.tools.slice(0, 3).map((tool) => (
              <span
                key={tool}
                className="px-1.5 py-0.5 rounded bg-muted text-[10px] text-muted-foreground border"
              >
                {tool}
              </span>
            ))}
          </div>

          <div className="flex items-center gap-1.5 pl-2 border-l">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span className="text-[11px] font-medium text-muted-foreground">Ready</span>
          </div>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-hidden">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center p-6">
            <div className="h-14 w-14 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mb-4 border border-primary/20 shadow-sm">
              {(() => {
                const Icon = currentAgent.icon;
                return <Icon className="h-7 w-7 stroke-[1.8]" aria-hidden="true" />;
              })()}
            </div>
            <h3 className="text-lg font-semibold mb-1 text-foreground">
              {currentAgent.name}
            </h3>
            <p className="text-xs text-primary font-medium mb-2">
              {currentAgent.tagline}
            </p>
            <p className="text-xs text-muted-foreground max-w-md mb-6 leading-relaxed">
              {currentAgent.description}
            </p>

            <div className="w-full max-w-md space-y-2 text-left">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground px-1">
                <Sparkles className="h-3 w-3 text-primary" />
                <span>Suggested Questions for {currentAgent.shortName}</span>
              </div>
              <div className="grid grid-cols-1 gap-2">
                {currentAgent.suggestedQuestions.map((q) => (
                  <Button
                    key={q}
                    variant="outline"
                    size="sm"
                    className="text-xs h-auto py-2 px-3 justify-start text-left whitespace-normal leading-relaxed hover:bg-primary/5 hover:border-primary/40 transition-colors"
                    onClick={() => handleSend(q)}
                  >
                    <span className="mr-2 text-primary">›</span>
                    {q}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <ScrollArea className="h-full">
            <div className="space-y-4 p-4">
              {messages.map((msg) => (
                <ChatMessage
                  key={msg.id}
                  message={msg}
                  onAcceptHandoff={handleAcceptHandoff}
                  onHandoffFinding={handleHandoffFinding}
                  onViewEvidence={onViewEvidence}
                />
              ))}
              {isStreaming && (
                <div className="flex items-center gap-2 text-xs text-muted-foreground p-4 bg-muted/20 rounded-md border w-fit">
                  <div className="h-2 w-2 bg-primary rounded-full animate-ping" />
                  <span>{currentAgent.name} analyzing case data...</span>
                </div>
              )}
            </div>
          </ScrollArea>
        )}
      </div>

      <ChatInput
        onSend={handleSend}
        onStop={handleStop}
        isStreaming={isStreaming}
        placeholder={`Ask ${currentAgent.name}... (e.g., "${currentAgent.suggestedQuestions[0]}")`}
      />
    </div>
  );
}
