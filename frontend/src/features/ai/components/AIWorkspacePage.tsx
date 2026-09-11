"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
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

export default function AIWorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params.caseId as string | undefined;
  const [activeSideTab, setActiveSideTab] = useState<
    "findings" | "agents" | "actions" | "correlations" | "summary" | "citations" | "evidence" | "graph" | "timeline"
  >("findings");

  useEffect(() => {
    if (!caseId) {
      router.push("/cases");
    }
  }, [caseId, router]);

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
          <h1 className="text-sm font-semibold">AI Intelligence Workspace</h1>
          <div className="ml-auto flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500" title="Backend connected" />
            <span className="text-[10px] text-muted-foreground">Live</span>
          </div>
        </div>

        <div className="flex-1 flex min-h-0">
          <div className="flex-1 min-w-0">
            <ChatPanel caseId={caseId} />
          </div>

          <div className="w-[420px] border-l flex flex-col min-h-0">
            <Tabs
              value={activeSideTab}
              onValueChange={(v) => setActiveSideTab(v as typeof activeSideTab)}
              className="flex flex-col h-full"
            >
              <TabsList className="grid grid-cols-5 h-9 mx-2 mt-2 w-[calc(100%-16px)]">
                <TabsTrigger value="findings" className="text-[9px] gap-0.5 px-1">
                  <Brain className="h-3 w-3" />
                  Findings
                </TabsTrigger>
                <TabsTrigger value="agents" className="text-[9px] gap-0.5 px-1">
                  <Cpu className="h-3 w-3" />
                  Agents
                </TabsTrigger>
                <TabsTrigger value="actions" className="text-[9px] gap-0.5 px-1">
                  <Lightbulb className="h-3 w-3" />
                  Actions
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
                  { key: "evidence" as const, icon: <FileText className="h-2.5 w-2.5" />, label: "Evidence" },
                  { key: "graph" as const, icon: <GitBranch className="h-2.5 w-2.5" />, label: "KG" },
                  { key: "timeline" as const, icon: <CalendarClock className="h-2.5 w-2.5" />, label: "Timeline" },
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
                <TabsContent value="findings" className="h-full mt-0">
                  <FindingsPanel caseId={caseId} />
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
      </div>
    </div>
  );
}
