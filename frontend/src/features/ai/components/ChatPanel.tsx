"use client";

import { useCallback, useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { MessageSquare } from "lucide-react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { useAIStore, type AIMessage } from "../store/aiStore";
import { useAIQuery } from "../hooks/useAIWorkspace";

export function ChatPanel({ caseId }: { caseId?: string }) {
  const {
    conversations,
    activeConversationId,
    isStreaming,
    addUserMessage,
    addAssistantMessage,
    setStreaming,
    createConversation,
  } = useAIStore();

  const scrollRef = useRef<HTMLDivElement>(null);
  const aiQuery = useAIQuery();

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId,
  );

  const messages = activeConversation?.messages ?? [];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages.length]);

  const handleSend = useCallback(
    async (content: string) => {
      let convId = activeConversationId;
      if (!convId) {
        convId = createConversation(caseId);
      }

      addUserMessage(convId, content);
      setStreaming(true);

      try {
        const response = await aiQuery.mutateAsync({
          query: content,
          case_id: caseId,
          top_k: 10,
        });

        const resultText =
          response.results && response.results.length > 0
            ? response.results
                .map(
                  (r, i) =>
                    `[${i + 1}] ${r.snippet || r.text || "No content available"}\n` +
                    (r.evidence_id ? `Source: Evidence ${r.evidence_id.slice(0, 8)}` : ""),
                )
                .join("\n\n")
            : "No relevant results found in the case database. Try uploading more evidence or processing existing evidence first.";

        const citations: AIMessage["citations"] =
          response.results?.map((r, i) => ({
            id: `cite-${i}`,
            type: "evidence" as const,
            label: r.evidence_id
              ? `Evidence ${r.evidence_id.slice(0, 8)}`
              : `Result ${i + 1}`,
            source_id: r.evidence_id || r.document_id,
            confidence: r.score,
          })) ?? [];

        const evidenceRefs =
          response.results
            ?.filter((r) => r.evidence_id)
            .map((r) => r.evidence_id!) ?? [];

        addAssistantMessage(convId, resultText, {
          citations,
          evidence_refs: evidenceRefs,
          confidence:
            response.results?.length > 0
              ? response.results.reduce((max, r) => Math.max(max, r.score), 0)
              : undefined,
        });
      } catch (error: unknown) {
        const errMsg =
          error instanceof Error ? error.message : "Unknown error occurred";
        addAssistantMessage(
          convId,
          `Error: Failed to get AI response. ${errMsg}\n\nPlease check if the backend is running and try again.`,
          { confidence: 0 },
        );
      } finally {
        setStreaming(false);
      }
    },
    [
      activeConversationId,
      caseId,
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
      <div ref={scrollRef} className="flex-1 overflow-hidden">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center p-6">
            <MessageSquare className="h-12 w-12 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Investigation AI</h3>
            <p className="text-sm text-muted-foreground max-w-sm mb-4">
              Ask questions about this investigation. The AI searches through
              evidence, entities, relationships, and timeline data from the
              case database.
            </p>
            <div className="grid grid-cols-2 gap-2 max-w-sm w-full">
              {[
                "Summarize key findings",
                "What entities were detected?",
                "Show timeline events",
                "What correlations exist?",
              ].map((q) => (
                <Button
                  key={q}
                  variant="outline"
                  size="sm"
                  className="text-xs h-auto py-2 justify-start text-left"
                  onClick={() => handleSend(q)}
                >
                  {q}
                </Button>
              ))}
            </div>
          </div>
        ) : (
          <ScrollArea className="h-full">
            <div className="space-y-4 p-4">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              {isStreaming && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground p-4">
                  <div className="h-2 w-2 bg-primary rounded-full animate-pulse" />
                  Analyzing case data...
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
        placeholder="Ask about evidence, entities, timeline, correlations..."
      />
    </div>
  );
}
