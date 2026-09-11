"use client";

import { useEffect } from "react";
import { useParams } from "next/navigation";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { RefreshCw } from "lucide-react";
import { useWorkspace } from "@/hooks/queries/useWorkspace";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { CaseSummaryBar } from "./CaseSummaryBar";
import { EvidenceExplorer } from "./EvidenceExplorer";
import { InvestigationCanvas } from "./InvestigationCanvas";
import { RightPanel } from "./RightPanel";
import { BottomPanel } from "./BottomPanel";

function WorkspaceContent({ caseId }: { caseId: string }) {
  const { data: workspace, isLoading, refetch } = useWorkspace(caseId);
  const { setCaseId } = useWorkspaceStore();

  useEffect(() => {
    setCaseId(caseId);
  }, [caseId, setCaseId]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-12 w-full" />
        <div className="h-[calc(100vh-12rem)] flex gap-4">
          <Skeleton className="w-1/4 h-full" />
          <Skeleton className="w-1/2 h-full" />
          <Skeleton className="w-1/4 h-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Investigation Workspace</h1>
          <p className="text-sm text-muted-foreground">
            {workspace?.case?.title ?? `Case ${caseId}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()} className="gap-1">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
        </div>
      </div>

      <CaseSummaryBar caseId={caseId} />

      <div className="h-[calc(100vh-16rem)] w-full border rounded-lg overflow-hidden bg-background">
        <ResizablePanelGroup orientation="vertical" className="h-full">
          <ResizablePanel defaultSize={70} minSize={40}>
            <ResizablePanelGroup orientation="horizontal" className="h-full">
              <ResizablePanel defaultSize={20} minSize={15} collapsible collapsedSize={0}>
                <EvidenceExplorer caseId={caseId} />
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={55} minSize={30}>
                <InvestigationCanvas caseId={caseId} />
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={25} minSize={20} collapsible collapsedSize={0}>
                <RightPanel caseId={caseId} />
              </ResizablePanel>
            </ResizablePanelGroup>
          </ResizablePanel>
          <ResizableHandle withHandle />
          <ResizablePanel defaultSize={30} minSize={15} collapsible collapsedSize={0}>
            <BottomPanel caseId={caseId} />
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
}

export function WorkspaceLayout({ caseId: propCaseId }: { caseId?: string } = {}) {
  const params = useParams();
  const caseId = propCaseId ?? (params?.caseId as string);

  return <WorkspaceContent caseId={caseId} />;
}
