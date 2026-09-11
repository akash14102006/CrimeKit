"use client";

import { ArrowLeft, HardDrive, Play, Pause, FileImage, Shield, Clock } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useDiskAnalyzerStore, type DiskAnalyzerView } from "../store/diskAnalyzerStore";
import type { Evidence } from "@/types/evidence";
import type { TSKCapabilities } from "@/types/tsk";
import { formatBytes } from "@/lib/utils";

interface DiskAnalyzerHeaderProps {
  evidence: Evidence | undefined;
  capabilities: TSKCapabilities | undefined;
  onProcess: () => void;
  isProcessing: boolean;
}

const views: { key: DiskAnalyzerView; label: string }[] = [
  { key: "partitions", label: "Partitions & Files" },
  { key: "timeline", label: "Timeline" },
  { key: "artifacts", label: "Artifacts" },
  { key: "entities", label: "Entities" },
  { key: "kg", label: "Knowledge Graph" },
  { key: "provenance", label: "Provenance" },
];

export function DiskAnalyzerHeader({ evidence, capabilities, onProcess, isProcessing }: DiskAnalyzerHeaderProps) {
  const store = useDiskAnalyzerStore();
  const { activeView } = store;
  const stage = store.processingStage;
  const evidenceMetadata = evidence?.metadata as Record<string, unknown> | null | undefined;
  const imageFormat = evidenceMetadata?.image_format as string | undefined;
  const ewfReason = capabilities?.ewf?.reason;
  const canAnalyze = Boolean(
    capabilities?.pytsk_available &&
    (!imageFormat?.toLowerCase().includes("ewf") || capabilities.libewf_available),
  );

  return (
    <div className="border-b bg-card px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/evidence" className="text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <HardDrive className="h-5 w-5 text-primary" />
          <div>
            <h1 className="text-lg font-semibold leading-tight">
              {evidence?.filename ?? "Disk Analyzer"}
            </h1>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>{evidence?.id}</span>
              {evidence?.size != null && (
                <>
                  <span className="text-border">|</span>
                  <span>{formatBytes(evidence.size)}</span>
                </>
              )}
              {evidence?.sha256 && (
                <>
                  <span className="text-border">|</span>
                  <span className="font-mono">{evidence.sha256.slice(0, 16)}...</span>
                </>
              )}
              {imageFormat && (
                <>
                  <span className="text-border">|</span>
                  <span>{imageFormat}</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {capabilities?.pytsk_available ? (
            <Badge variant="outline" className="gap-1 text-xs">
              <Shield className="h-3 w-3" />
              pytsk3 {capabilities.tsk_version}
            </Badge>
          ) : (
            <Badge variant="destructive" className="gap-1 text-xs">
              TSK Unavailable
            </Badge>
          )}
          {capabilities?.libewf_available && (
            <Badge variant="outline" className="gap-1 text-xs">
              <FileImage className="h-3 w-3" />
              libewf
            </Badge>
          )}
          {!canAnalyze && ewfReason && (
            <span className="max-w-[280px] text-right text-xs text-destructive">{ewfReason}</span>
          )}
          {store.metrics && (
            <Badge variant="secondary" className="gap-1 text-xs">
              <Clock className="h-3 w-3" />
              {(store.metrics.processing_time_ms / 1000).toFixed(1)}s
            </Badge>
          )}
          <Separator orientation="vertical" className="h-6" />
          <Button
            size="sm"
            onClick={onProcess}
            disabled={isProcessing || !evidence?.case_id || !canAnalyze}
            className="gap-1"
          >
            {isProcessing ? (
              <>
                <Pause className="h-3.5 w-3.5" />
                Processing{stage ? `: ${stage.replace(/_/g, " ")}` : "..."}
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5" />
                Run TSK Analysis
              </>
            )}
          </Button>
        </div>
      </div>

      <nav className="mt-3 flex gap-1 border-b border-transparent">
        {views.map((v) => (
          <button
            key={v.key}
            onClick={() => store.setActiveView(v.key)}
            className={`rounded-t-md px-3 py-1.5 text-xs font-medium transition-colors ${
              activeView === v.key
                ? "border-b-2 border-primary bg-primary/5 text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {v.label}
          </button>
        ))}
      </nav>
    </div>
  );
}
