"use client";

import { memo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  CheckCircle2,
  Loader2,
  Circle,
  XCircle,
  Clock,
  GitBranch,
} from "lucide-react";
import type { JobProgress } from "@/types/processing";

const PIPELINE_STAGES = [
  "Integrity Verification",
  "Metadata Extraction",
  "Hash Verification",
  "OCR",
  "Thumbnail Generation",
  "AI Pipeline",
  "Knowledge Graph",
  "Timeline Extraction",
  "Entity Extraction",
  "Correlation",
  "Final Report",
];

function StageIcon({ status }: { status: "completed" | "running" | "pending" | "failed" | "skipped" }) {
  switch (status) {
    case "completed":
      return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
    case "running":
      return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
    case "failed":
      return <XCircle className="h-4 w-4 text-destructive" />;
    case "skipped":
      return <Circle className="h-4 w-4 text-muted-foreground/30" />;
    default:
      return <Circle className="h-4 w-3 text-muted-foreground/50" />;
  }
}

function getStageStatus(
  stageName: string,
  completedProcessors: string[],
  currentProcessor?: string,
): "completed" | "running" | "pending" | "failed" {
  const normalized = stageName.toLowerCase().replace(/\s+/g, "_");
  const completed = completedProcessors.map((p) => p.toLowerCase().replace(/\s+/g, "_"));

  if (completed.includes(normalized)) return "completed";
  if (
    currentProcessor &&
    currentProcessor.toLowerCase().replace(/\s+/g, "_") === normalized
  ) {
    return "running";
  }
  return "pending";
}

export const ProcessingPipeline = memo(function ProcessingPipeline({
  progress,
}: {
  progress?: JobProgress;
}) {
  const completedProcessors = progress?.completed_processors ?? [];
  const currentProcessor = progress?.processors?.find(
    (p) => !completedProcessors.includes(p),
  );

  const completedCount = completedProcessors.length;
  const totalStages = progress?.processors?.length ?? PIPELINE_STAGES.length;
  const overallProgress = totalStages > 0 ? Math.round((completedCount / totalStages) * 100) : 0;

  const stages = (progress?.processors?.length ?? 0) > 0
    ? progress!.processors
    : PIPELINE_STAGES;

  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <GitBranch className="h-4 w-4" />
          Processing Pipeline
          {progress && (
            <Badge variant="secondary" className="text-[10px]">
              {completedCount}/{totalStages} stages
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {progress ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span>Overall Progress</span>
              <span className="text-muted-foreground">{overallProgress}%</span>
            </div>
            <Progress value={overallProgress} className="h-2" />

            <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
              {progress.queued_at && (
                <span>Queued: {new Date(progress.queued_at).toLocaleTimeString()}</span>
              )}
              {progress.started_at && (
                <span>Started: {new Date(progress.started_at).toLocaleTimeString()}</span>
              )}
              {progress.finished_at && (
                <span>Finished: {new Date(progress.finished_at).toLocaleTimeString()}</span>
              )}
            </div>

            <div className="space-y-1">
              {stages.map((stage, i) => {
                const status = getStageStatus(
                  stage,
                  completedProcessors,
                  currentProcessor,
                );
                return (
                  <div
                    key={`${stage}-${i}`}
                    className={`flex items-center gap-2 py-1.5 px-2 rounded text-xs ${
                      status === "completed"
                        ? "bg-emerald-50"
                        : status === "running"
                          ? "bg-blue-50"
                          : status === "failed"
                            ? "bg-red-50"
                            : ""
                    }`}
                  >
                    <StageIcon status={status} />
                    <span
                      className={`flex-1 ${
                        status === "pending" ? "text-muted-foreground" : ""
                      }`}
                    >
                      {stage}
                    </span>
                    {status === "completed" && (
                      <Badge variant="outline" className="text-[8px] text-emerald-600">
                        Done
                      </Badge>
                    )}
                    {status === "running" && (
                      <Badge variant="outline" className="text-[8px] text-blue-600">
                        Running
                      </Badge>
                    )}
                    {i < stages.length - 1 && status !== "pending" && (
                      <div className="absolute left-[1.35rem] mt-6 w-px h-2 bg-border" />
                    )}
                  </div>
                );
              })}
            </div>

            {progress.error != null && (
              <div className="p-2 rounded bg-red-50 border border-red-200">
                <p className="text-xs text-destructive">{String(progress.error)}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-4">
            <GitBranch className="h-6 w-6 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-xs text-muted-foreground">
              Select a job to view the processing pipeline
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
});
