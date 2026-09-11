"use client";

import { useParams } from "next/navigation";
import { useEffect } from "react";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingState } from "@/components/shared/LoadingState";
import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";
import { useEvidenceDetail, useTSKProcess, useTSKCapabilities } from "../hooks/useDiskAnalyzer";
import { useTSKRealtime } from "../hooks/useTSKRealtime";
import { DiskAnalyzerHeader } from "./DiskAnalyzerHeader";
import { PipelineProgress } from "./PipelineProgress";
import { PartitionExplorer } from "./PartitionExplorer";
import { FileDetailsPanel } from "./FileDetailsPanel";
import { ForensicMetrics } from "./ForensicMetrics";
import { ArtifactTimeline } from "./ArtifactTimeline";
import { EntitiesPanel } from "./EntitiesPanel";
import { ProvenanceTrace } from "./ProvenanceTrace";
import { KGPanel } from "./KGPanel";
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from "@/components/ui/resizable";

export function DiskAnalyzerPage() {
  const params = useParams();
  const evidenceId = params.evidenceId as string;
  const store = useDiskAnalyzerStore();
  const { data: evidence, isLoading: evidenceLoading, isError: evidenceError, refetch: refetchEvidence } =
    useEvidenceDetail(evidenceId);
  const processMutation = useTSKProcess();
  const { data: capabilities } = useTSKCapabilities();

  useTSKRealtime(evidence?.case_id ?? null, evidenceId);

  useEffect(() => {
    store.setEvidenceId(evidenceId);
    if (evidence?.case_id) {
      store.setCaseId(evidence.case_id);
    }
  }, [evidenceId, evidence, store]);

  const handleProcess = () => {
    if (!evidence?.case_id) return;
    processMutation.mutate({
      evidence_id: evidenceId,
      case_id: evidence.case_id,
      sync: true,
    });
  };

  if (evidenceError) {
    return (
      <AuthGuard allowedRoles={["admin", "investigator", "analyst", "viewer"]}>
        <div className="space-y-6 p-6">
          <ErrorState
            title="Evidence not found"
            description="The evidence item could not be loaded. Verify the evidence ID and try again."
            onRetry={() => refetchEvidence()}
          />
        </div>
      </AuthGuard>
    );
  }

  if (evidenceLoading) {
    return (
      <AuthGuard allowedRoles={["admin", "investigator", "analyst", "viewer"]}>
        <LoadingState label="Loading evidence..." />
      </AuthGuard>
    );
  }

  const activeView = store.activeView;

  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst", "viewer"]}>
      <div className="flex h-full flex-col">
        <DiskAnalyzerHeader
          evidence={evidence}
          capabilities={capabilities}
          onProcess={handleProcess}
          isProcessing={store.processing}
        />

        <PipelineProgress />

        <div className="flex-1 overflow-hidden px-4 pb-4">
          <ResizablePanelGroup orientation="horizontal" className="h-full rounded-lg border">
            <ResizablePanel defaultSize={35} minSize={25}>
              <PartitionExplorer />
            </ResizablePanel>

            <ResizableHandle withHandle />

            <ResizablePanel defaultSize={65} minSize={40}>
              <ResizablePanelGroup orientation="vertical">
                <ResizablePanel defaultSize={60} minSize={30}>
                  {activeView === "partitions" && <FileDetailsPanel />}
                  {activeView === "timeline" && <ArtifactTimeline />}
                  {activeView === "artifacts" && <FileDetailsPanel />}
                  {activeView === "entities" && <EntitiesPanel />}
                  {activeView === "kg" && <KGPanel />}
                  {activeView === "provenance" && <ProvenanceTrace />}
                </ResizablePanel>

                <ResizableHandle withHandle />

                <ResizablePanel defaultSize={40} minSize={20}>
                  <ForensicMetrics />
                </ResizablePanel>
              </ResizablePanelGroup>
            </ResizablePanel>
          </ResizablePanelGroup>
        </div>
      </div>
    </AuthGuard>
  );
}
