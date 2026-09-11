"use client";

import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { CalendarClock, ExternalLink } from "lucide-react";
import { useWorkspaceTimeline } from "@/hooks/queries/useWorkspace";

export function TimelineReferencesPanel({ caseId }: { caseId: string }) {
  const { data: timeline, isLoading } = useWorkspaceTimeline(caseId);

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <CalendarClock className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-semibold">Timeline References</h3>
          {timeline && timeline.length > 0 && (
            <Badge variant="secondary" className="text-[10px]">
              {timeline.length}
            </Badge>
          )}
        </div>
        <a
          href="/timeline"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-primary hover:underline flex items-center gap-1"
        >
          Open Timeline
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-2">
          {!timeline || timeline.length === 0 ? (
            <div className="text-center py-12">
              <CalendarClock className="h-12 w-12 mx-auto text-muted-foreground/20 mb-3" />
              <h4 className="text-sm font-medium mb-1">No Timeline Events</h4>
              <p className="text-xs text-muted-foreground max-w-xs mx-auto">
                Process evidence to extract timeline events and build a
                chronological view of the investigation.
              </p>
            </div>
          ) : (
            timeline.map((event, i) => (
              <div
                key={`${event.source_type}-${event.source_id ?? i}`}
                className="flex gap-3 p-2 rounded-md hover:bg-muted/30 transition-colors"
              >
                <div className="flex flex-col items-center">
                  <div className="h-2.5 w-2.5 rounded-full bg-primary shrink-0" />
                  {i < timeline.length - 1 && (
                    <div className="w-px flex-1 bg-border mt-1" />
                  )}
                </div>
                <div className="pb-3 flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium">{event.summary}</span>
                    <span className="text-[10px] text-muted-foreground">
                      {event.date || event.timestamp}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <Badge variant="outline" className="text-[9px]">
                      {event.source_type}
                    </Badge>
                    {event.source_id && (
                      <a
                        href={`/evidence/${event.source_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[10px] text-primary hover:underline inline-flex items-center gap-1"
                      >
                        Evidence {event.source_id.slice(0, 8)}...
                        <ExternalLink className="h-2 w-2" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
