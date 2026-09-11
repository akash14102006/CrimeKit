"use client";

import { Clock, FileText, Upload, AlertTriangle } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useCaseTimeline } from "@/hooks/queries/useTimeline";

interface CaseTimelinePreviewProps {
  caseId: string;
}

const sourceIcons: Record<string, React.ReactNode> = {
  evidence_upload: <Upload className="h-3.5 w-3.5" />,
  case_created: <FileText className="h-3.5 w-3.5" />,
  alert: <AlertTriangle className="h-3.5 w-3.5" />,
};

export function CaseTimelinePreview({ caseId }: CaseTimelinePreviewProps) {
  const { data: events, isLoading, isError } = useCaseTimeline(caseId);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="h-8 w-8 rounded-full shrink-0" />
            <div className="flex-1 space-y-1">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <p className="text-sm text-muted-foreground">
        Failed to load timeline.
      </p>
    );
  }

  const items = events?.slice(0, 5) ?? [];

  if (items.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No timeline events yet.
      </p>
    );
  }

  return (
    <div className="relative space-y-3">
      <div className="absolute left-4 top-2 bottom-2 w-px bg-border" aria-hidden="true" />
      {items.map((event) => (
        <div key={event.id} className="relative flex gap-3">
          <div className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full bg-muted text-muted-foreground">
            {sourceIcons[event.source] ?? <Clock className="h-3.5 w-3.5" />}
          </div>
          <div className="flex-1 min-w-0 pt-1">
            <p className="text-sm font-medium truncate">{event.title}</p>
            <p className="text-xs text-muted-foreground truncate">
              {event.description}
            </p>
            <time className="text-xs text-muted-foreground">
              {event.timestamp
                ? new Date(event.timestamp).toLocaleDateString()
                : "Unknown date"}
            </time>
          </div>
        </div>
      ))}
    </div>
  );
}
