"use client";

import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import type { TSKProcessingStage } from "@/types/tsk";

const STAGE_LABELS: Record<TSKProcessingStage, string> = {
  evidence_accepted: "Accepted",
  sha256_verified: "SHA-256",
  image_capability_detected: "Format",
  image_opened: "Opened",
  volume_system_detected: "Volumes",
  partition_discovery: "Partitions",
  filesystem_detection: "FS Detect",
  filesystem_opened: "FS Open",
  root_directory_discovery: "Root",
  directory_traversal: "Traverse",
  file_enumeration: "Enumerate",
  metadata_extraction: "Metadata",
  allocation_classification: "Allocation",
  deleted_orphan_analysis: "Deleted",
  filesystem_temporal_extraction: "Temporal",
  artifact_extraction: "Extract",
  artifact_normalization: "Normalize",
  timeline_generation: "Timeline",
  text_routing: "Text Route",
  entity_extraction: "Entities",
  entity_resolution: "Resolve",
  relationship_discovery: "Relationships",
  neo4j_enrichment: "Neo4j",
  search_indexing: "Index",
  processing_complete: "Complete",
};

const STAGES: TSKProcessingStage[] = [
  "evidence_accepted",
  "sha256_verified",
  "image_capability_detected",
  "image_opened",
  "volume_system_detected",
  "partition_discovery",
  "filesystem_detection",
  "filesystem_opened",
  "root_directory_discovery",
  "directory_traversal",
  "file_enumeration",
  "metadata_extraction",
  "allocation_classification",
  "deleted_orphan_analysis",
  "filesystem_temporal_extraction",
  "artifact_extraction",
  "artifact_normalization",
  "timeline_generation",
  "text_routing",
  "entity_extraction",
  "entity_resolution",
  "relationship_discovery",
  "neo4j_enrichment",
  "search_indexing",
  "processing_complete",
];

export function PipelineProgress() {
  const { processing, processingStage, stagesCompleted, stagesFailed, progressPercent } =
    useDiskAnalyzerStore();

  if (!processing && stagesCompleted.length === 0) return null;

  return (
    <div className="border-b bg-card px-4 py-2">
      <div className="mb-1.5 flex items-center justify-between text-xs text-muted-foreground">
        <span>TSK Pipeline</span>
        <span>{progressPercent}%</span>
      </div>
      <Progress value={progressPercent} className="mb-2 h-1.5" />
      <div className="flex flex-wrap gap-1">
        {STAGES.map((stage) => {
          const isCompleted = stagesCompleted.includes(stage);
          const isFailed = stagesFailed.includes(stage);
          const isCurrent = processingStage === stage;

          return (
            <div
              key={stage}
              className={cn(
                "rounded px-1.5 py-0.5 text-[10px] font-medium transition-colors",
                isCompleted && "bg-success/10 text-success",
                isFailed && "bg-destructive/10 text-destructive",
                isCurrent && "bg-primary/10 text-primary ring-1 ring-primary/30",
                !isCompleted && !isFailed && !isCurrent && "bg-muted text-muted-foreground/50",
              )}
            >
              {STAGE_LABELS[stage]}
            </div>
          );
        })}
      </div>
    </div>
  );
}
