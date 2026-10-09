"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import {
  Brain,
  Lightbulb,
  Cpu,
  GitBranch,
  BookOpen,
  FileText,
  CalendarClock,
  ChevronLeft,
  Loader2,
} from "lucide-react";
import { ChatPanel } from "../components/ChatPanel";
import { ChatSidebar } from "../components/ChatSidebar";
import { FindingsPanel } from "../components/FindingsPanel";
import { AgentStatusPanel } from "../components/AgentStatusPanel";
import { SuggestedActionsPanel } from "../components/SuggestedActionsPanel";
import { CorrelationPanel } from "../components/CorrelationPanel";
import { InvestigationSummaryPanel } from "../components/InvestigationSummaryPanel";
import { CitationsPanel } from "../components/CitationsPanel";
import { EvidenceReferencesPanel } from "../components/EvidenceReferencesPanel";
import { GraphReferencesPanel } from "../components/GraphReferencesPanel";
import { TimelineReferencesPanel } from "../components/TimelineReferencesPanel";

import { AgentSelector } from "./AgentSelector";
import { useAIStore } from "../store/aiStore";
import type { AgentId } from "../constants/agentRegistry";
import { aiService } from "@/services/aiService";

import { ContradictionMatrixPanel } from "./ContradictionMatrixPanel";
import { CaseArchivePanel } from "./CaseArchivePanel";
import { LiveInvestigationDashboard } from "./LiveInvestigationDashboard";
import { CaseContextPanel } from "./CaseContextPanel";
import { AlertTriangle, ShieldCheck, FolderKanban } from "lucide-react";

export default function AIWorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params.caseId as string | undefined;
  const {
    selectedAgentId,
    setSelectedAgentId,
    createConversation,
    conversations,
    activeConversationId,
    setActiveConversation,
    syncSessions,
  } = useAIStore();
  const [viewMode, setViewMode] = useState<"chat" | "live-dashboard">("chat");
  const [activeSideTab, setActiveSideTab] = useState<
    "context" | "findings" | "contradictions" | "agents" | "actions" | "correlations" | "summary" | "archive" | "evidence" | "graph" | "timeline" | "citations"
  >("context");

  useEffect(() => {
    if (!caseId) {
      router.push("/cases");
      return;
    }

    // Sync backend sessions for this case
    aiService
      .listSessions({ case_id: caseId })
      .then((res) => {
        if (res?.items && res.items.length > 0) {
          syncSessions(
            res.items.map((s) => ({
              id: s.id,
              title: s.title,
              case_id: s.case_id,
              agent_id: s.agent_id,
              updated_at: s.updated_at,
              pinned: s.pinned,
            })),
          );
        }
      })
      .catch(() => {
        // Fallback to local store
      });
  }, [caseId, router, syncSessions]);

  const handleSelectAgent = (agentId: AgentId) => {
    setSelectedAgentId(agentId);
    // Find matching session for this case & agent, or create one
    const matchingConv = conversations.find(
      (c) => c.case_id === caseId && c.agent_id === agentId,
    );
    if (matchingConv) {
      setActiveConversation(matchingConv.id);
    } else {
      createConversation(caseId, agentId);
    }
  };

  if (!caseId) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <ChatSidebar caseId={caseId} />

      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex items-center gap-3 px-4 py-2 border-b bg-background">
          <Button
            variant="ghost"
            size="sm"
            className="h-8 gap-1"
            onClick={() => router.push(`/workspace/${caseId}`)}
          >
            <ChevronLeft className="h-4 w-4" />
            Workspace
          </Button>
          <div className="h-4 w-px bg-border" />
          <Brain className="h-4 w-4 text-primary" />
          <div className="flex items-center gap-2 min-w-0">
            <h1 className="text-sm font-semibold truncate">AI Investigation Workspace</h1>
            <span className="text-[11px] font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded shrink-0">
              {caseId}
            </span>
          </div>
          <div className="ml-auto flex items-center gap-2">
            {/* View Mode Toggle */}
            <div className="flex items-center rounded-md border bg-muted/30 p-0.5 text-xs font-medium">
              <button
                type="button"
                onClick={() => setViewMode("live-dashboard")}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-sm transition-colors text-[11px] ${
                  viewMode === "live-dashboard"
                    ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <Cpu className="h-3 w-3" />
                Live Dashboard
              </button>
              <button
                type="button"
                onClick={() => setViewMode("chat")}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-sm transition-colors text-[11px] ${
                  viewMode === "chat"
                    ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <Brain className="h-3 w-3" />
                Specialist Chat
              </button>
            </div>

            <Badge variant="outline" className="text-[10px] bg-background border-primary/30 font-mono gap-1">
              <span className="text-muted-foreground">Provider:</span>
              <span className="font-semibold text-primary">Nebius</span>
              <span className="text-muted-foreground">·</span>
              <span className="text-foreground">Nemotron</span>
            </Badge>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-muted/40 border text-[10px]">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              <span className="font-semibold text-amber-600">DETERMINISTIC / AUDIT MODE</span>
            </div>
          </div>
        </div>

        {viewMode === "live-dashboard" ? (
          <div className="flex-1 min-h-0">
            <LiveInvestigationDashboard
              caseId={caseId}
              onOpenArchiveTab={() => {
                setViewMode("chat");
                setActiveSideTab("archive");
              }}
              onOpenMatrixTab={() => {
                setViewMode("chat");
                setActiveSideTab("contradictions");
              }}
            />
          </div>
        ) : (
          <>
            {/* Centralized Specialist Agent Selector Bar */}
            <AgentSelector
              selectedAgentId={selectedAgentId}
              onSelectAgent={handleSelectAgent}
            />

            <div className="flex-1 flex min-h-0">
              <div className="flex-1 min-w-0">
                <ChatPanel caseId={caseId} />
              </div>

          <div className="w-[440px] border-l flex flex-col min-h-0">
            <Tabs
              value={activeSideTab}
              onValueChange={(v) => setActiveSideTab(v as typeof activeSideTab)}
              className="flex flex-col h-full"
            >
              <TabsList className="grid grid-cols-6 h-9 mx-2 mt-2 w-[calc(100%-16px)]">
                <TabsTrigger value="context" className="text-[9px] gap-0.5 px-1 font-semibold text-primary">
                  <FolderKanban className="h-3 w-3" />
                  Context
                </TabsTrigger>
                <TabsTrigger value="findings" className="text-[9px] gap-0.5 px-1">
                  <Brain className="h-3 w-3" />
                  Findings
                </TabsTrigger>
                <TabsTrigger value="contradictions" className="text-[9px] gap-0.5 px-1 font-semibold text-amber-500">
                  <AlertTriangle className="h-3 w-3 text-amber-500" />
                  Matrix
                </TabsTrigger>
                <TabsTrigger value="agents" className="text-[9px] gap-0.5 px-1">
                  <Cpu className="h-3 w-3" />
                  Agents
                </TabsTrigger>
                <TabsTrigger value="correlations" className="text-[9px] gap-0.5 px-1">
                  <GitBranch className="h-3 w-3" />
                  Links
                </TabsTrigger>
                <TabsTrigger value="summary" className="text-[9px] gap-0.5 px-1">
                  <BookOpen className="h-3 w-3" />
                  Summary
                </TabsTrigger>
              </TabsList>

              <div className="flex gap-1 px-2 py-1 border-b">
                {[
                  { key: "archive" as const, icon: <ShieldCheck className="h-2.5 w-2.5 text-emerald-500" />, label: "Seal/Archive" },
                  { key: "evidence" as const, icon: <FileText className="h-2.5 w-2.5" />, label: "Evidence" },
                  { key: "graph" as const, icon: <GitBranch className="h-2.5 w-2.5" />, label: "KG" },
                  { key: "timeline" as const, icon: <CalendarClock className="h-2.5 w-2.5" />, label: "Timeline" },
                  { key: "actions" as const, icon: <Lightbulb className="h-2.5 w-2.5" />, label: "Actions" },
                  { key: "citations" as const, icon: <FileText className="h-2.5 w-2.5" />, label: "Citations" },
                ].map((item) => (
                  <button
                    key={item.key}
                    className={`flex items-center gap-1 px-2 py-1 rounded text-[10px] transition-colors ${
                      activeSideTab === item.key
                        ? "bg-muted font-medium"
                        : "text-muted-foreground hover:bg-muted/50"
                    }`}
                    onClick={() => setActiveSideTab(item.key)}
                  >
                    {item.icon}
                    {item.label}
                  </button>
                ))}
              </div>

              <div className="flex-1 overflow-hidden">
                <TabsContent value="context" className="h-full mt-0">
                  <CaseContextPanel
                    caseId={caseId}
                    selectedAgentId={selectedAgentId}
                    onOpenContradictions={() => setActiveSideTab("contradictions")}
                    onOpenArchive={() => setActiveSideTab("archive")}
                    onHandoffToAgent={handleSelectAgent}
                  />
                </TabsContent>
                <TabsContent value="findings" className="h-full mt-0">
                  <FindingsPanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="contradictions" className="h-full mt-0">
                  <ContradictionMatrixPanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="archive" className="h-full mt-0">
                  <CaseArchivePanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="agents" className="h-full mt-0">
                  <AgentStatusPanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="actions" className="h-full mt-0">
                  <SuggestedActionsPanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="correlations" className="h-full mt-0">
                  <CorrelationPanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="summary" className="h-full mt-0">
                  <InvestigationSummaryPanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="evidence" className="h-full mt-0">
                  <EvidenceReferencesPanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="graph" className="h-full mt-0">
                  <GraphReferencesPanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="timeline" className="h-full mt-0">
                  <TimelineReferencesPanel caseId={caseId} />
                </TabsContent>
                <TabsContent value="citations" className="h-full mt-0">
                  <CitationsPanel caseId={caseId} />
                </TabsContent>
              </div>
            </Tabs>
          </div>
        </div>
      </>
    )}
  </div>
</div>
  );
}

