"use client";

import Link from "next/link";
import { File, ExternalLink } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useCaseEvidence } from "@/hooks/queries/useEvidence";
import { OpenDiskAnalyzerAction } from "@/features/evidence/components/OpenDiskAnalyzerAction";
import type { Evidence } from "@/types/evidence";

interface CaseEvidenceSummaryProps {
  caseId: string;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function CaseEvidenceSummary({ caseId }: CaseEvidenceSummaryProps) {
  const { data: evidence, isLoading, isError } = useCaseEvidence(caseId);

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <Skeleton className="h-8 w-8 rounded" />
            <div className="flex-1 space-y-1">
              <Skeleton className="h-4 w-2/3" />
              <Skeleton className="h-3 w-1/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <p className="text-sm text-muted-foreground">
        Failed to load evidence.
      </p>
    );
  }

  const items = evidence ?? [];

  if (items.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No evidence uploaded yet.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {items.slice(0, 5).map((item) => (
        <div
          key={item.id}
          className="flex items-center gap-3 rounded-lg border p-2 hover:bg-muted/50 transition-colors"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded bg-muted">
            <File className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{item.filename}</p>
            <p className="text-xs text-muted-foreground">
              {formatFileSize(item.size)} &middot; {item.mime_type ?? "Unknown"}
            </p>
          </div>
          <OpenDiskAnalyzerAction evidence={item as Evidence} />
          <Link
            href={`/evidence`}
            className="text-muted-foreground hover:text-foreground transition-colors"
            aria-label={`View evidence ${item.filename}`}
          >
            <ExternalLink className="h-3.5 w-3.5" />
          </Link>
        </div>
      ))}
      {items.length > 5 && (
        <Link
          href={`/evidence`}
          className="block text-center text-sm text-primary hover:underline"
        >
          View all {items.length} evidence items
        </Link>
      )}
    </div>
  );
}
