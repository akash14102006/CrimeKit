"use client";

import { Clock, FileText } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";

const EVENT_COLORS: Record<string, string> = {
  file_created: "bg-success/10 text-success border-success/20",
  file_modified: "bg-info/10 text-info border-info/20",
  file_accessed: "bg-muted text-muted-foreground border-border",
  file_deleted: "bg-destructive/10 text-destructive border-destructive/20",
  directory_created: "bg-success/10 text-success border-success/20",
  metadata_changed: "bg-warning/10 text-warning border-warning/20",
};

function TimelineEventRow({ event }: { event: import("@/types/tsk").TSKTimelineEvent }) {
  const colorClass = EVENT_COLORS[event.event_type] ?? "bg-muted text-muted-foreground border-border";

  return (
    <div className="group flex items-start gap-3 py-2">
      <div className="flex flex-col items-center">
        <div className={`h-2.5 w-2.5 rounded-full border ${colorClass}`} />
        <div className="w-px flex-1 bg-border" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className={`text-[10px] ${colorClass}`}>
            {event.event_type.replace(/_/g, " ")}
          </Badge>
          <span className="text-[10px] text-muted-foreground">
            {new Date(event.timestamp).toLocaleString()}
          </span>
        </div>
        <p className="mt-0.5 flex items-center gap-1 text-xs">
          <FileText className="h-3 w-3 shrink-0 text-muted-foreground" />
          <span className="truncate font-mono">{event.file_path}</span>
        </p>
        <div className="mt-0.5 flex items-center gap-2 text-[10px] text-muted-foreground">
          <span>Confidence: {(event.confidence * 100).toFixed(0)}%</span>
          <span className="text-border">|</span>
          <span>Source: {event.source}</span>
        </div>
      </div>
    </div>
  );
}

export function ArtifactTimeline() {
  const { timeline } = useDiskAnalyzerStore();

  if (timeline.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-6 text-center">
        <Clock className="mb-2 h-8 w-8 text-muted-foreground/30" />
        <p className="text-xs text-muted-foreground">
          No timeline events detected. Run TSK analysis to generate a timeline.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b px-4 py-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Timeline ({timeline.length} events)
        </h3>
        <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
          <Badge variant="outline" className="gap-1 text-[10px]">
            <div className="h-1.5 w-1.5 rounded-full bg-success" />
            Created
          </Badge>
          <Badge variant="outline" className="gap-1 text-[10px]">
            <div className="h-1.5 w-1.5 rounded-full bg-info" />
            Modified
          </Badge>
          <Badge variant="outline" className="gap-1 text-[10px]">
            <div className="h-1.5 w-1.5 rounded-full bg-destructive" />
            Deleted
          </Badge>
        </div>
      </div>
      <ScrollArea className="flex-1 px-4">
        <div className="py-2">
          {timeline
            .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
            .slice(0, 200)
            .map((event) => (
              <TimelineEventRow key={event.event_id} event={event} />
            ))}
          {timeline.length > 200 && (
            <p className="py-2 text-center text-[10px] text-muted-foreground">
              Showing 200 of {timeline.length} events
            </p>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
