"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Clock, Upload, Cpu, Brain, Shield, FileText, Activity } from "lucide-react";
import { useTimelineStore } from "../store/timelineStore";
import type { TimelineEvent } from "@/types/timeline";

const SOURCE_ICONS: Record<string, typeof Clock> = {
  forensic_engine: Cpu,
  text_extraction: FileText,
  ocr: FileText,
  evidence: Upload,
  processing: Cpu,
  custody: Shield,
  ai: Brain,
  system: Activity,
};

const SOURCE_COLORS: Record<string, string> = {
  forensic_engine: "border-blue-500 bg-blue-500/10",
  text_extraction: "border-purple-500 bg-purple-500/10",
  ocr: "border-cyan-500 bg-cyan-500/10",
  evidence: "border-emerald-500 bg-emerald-500/10",
  processing: "border-orange-500 bg-orange-500/10",
  custody: "border-amber-500 bg-amber-500/10",
  ai: "border-pink-500 bg-pink-500/10",
  system: "border-gray-500 bg-gray-500/10",
};

function groupEventsByDate(events: TimelineEvent[]): Map<string, TimelineEvent[]> {
  const groups = new Map<string, TimelineEvent[]>();
  for (const event of events) {
    const dateStr = event.timestamp
      ? new Date(event.timestamp).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" })
      : "Unknown Date";
    const existing = groups.get(dateStr) ?? [];
    existing.push(event);
    groups.set(dateStr, existing);
  }
  return groups;
}

interface Props {
  events: TimelineEvent[];
  isLoading: boolean;
}

export function TimelineView({ events, isLoading }: Props) {
  const { selectedEventId, selectEvent, mode } = useTimelineStore();

  if (isLoading) {
    return (
      <div className="space-y-4 p-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <Skeleton className="h-10 w-10 rounded-full shrink-0" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-[200px]" />
              <Skeleton className="h-3 w-[300px]" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Clock className="h-12 w-12 text-muted-foreground mb-3 opacity-40" />
        <p className="text-sm font-medium">No timeline events</p>
        <p className="text-xs text-muted-foreground mt-1">Events will appear as evidence is processed and investigated</p>
      </div>
    );
  }

  if (mode === "grouped") {
    const grouped = groupEventsByDate(events);
    return (
      <ScrollArea className="h-full">
        <div className="p-4 space-y-6">
          {Array.from(grouped.entries()).map(([date, dateEvents]) => (
            <div key={date}>
              <div className="flex items-center gap-2 mb-3">
                <Badge variant="outline" className="text-[10px] font-medium">{date}</Badge>
                <span className="text-[10px] text-muted-foreground">{dateEvents.length} events</span>
                <div className="flex-1 h-px bg-border" />
              </div>
              <div className="space-y-2 ml-4">
                {dateEvents.map((event) => (
                  <EventCard
                    key={event.id}
                    event={event}
                    isSelected={selectedEventId === event.id}
                    onSelect={() => selectEvent(event.id)}
                    compact={false}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    );
  }

  const isCompact = mode === "compact";

  return (
    <ScrollArea className="h-full">
      <div className="p-4">
        <div className="relative">
          <div className="absolute left-5 top-0 bottom-0 w-px bg-border" />
          <div className="space-y-1">
            {events.map((event) => {
              const isSelected = selectedEventId === event.id;
              return (
                <div key={event.id} className="flex gap-3 relative group">
                  <div
                    className={`h-${isCompact ? "6" : "8"} w-${isCompact ? "6" : "8"} rounded-full flex items-center justify-center shrink-0 z-10 transition-all cursor-pointer ${
                      isSelected
                        ? `ring-2 ring-primary ring-offset-2 ${SOURCE_COLORS[event.source] ?? SOURCE_COLORS.system}`
                        : `${SOURCE_COLORS[event.source] ?? SOURCE_COLORS.system} hover:ring-2 hover:ring-primary/30 hover:ring-offset-1`
                    }`}
                    onClick={() => selectEvent(event.id)}
                  >
                    {(() => {
                      const Icon = SOURCE_ICONS[event.source] ?? Clock;
                      return <Icon className={`h-${isCompact ? "3" : "3.5"} w-${isCompact ? "3" : "3.5"} text-foreground`} />;
                    })()}
                  </div>
                  <div
                    className={`flex-1 min-w-0 rounded-lg border p-${isCompact ? "2" : "3"} transition-colors cursor-pointer ${
                      isSelected ? "bg-primary/5 border-primary/20" : "hover:bg-muted/30"
                    }`}
                    onClick={() => selectEvent(event.id)}
                  >
                    <div className="flex items-center gap-2">
                      <p className={`font-medium ${isCompact ? "text-[11px]" : "text-xs"} truncate`}>{event.title}</p>
                      {!isCompact && (
                        <Badge variant="outline" className="text-[9px] shrink-0">
                          {event.source}
                        </Badge>
                      )}
                    </div>
                    {!isCompact && (
                      <p className="text-[10px] text-muted-foreground mt-0.5 line-clamp-2">{event.description}</p>
                    )}
                    <div className="flex items-center gap-2 mt-1 text-[10px] text-muted-foreground">
                      <Clock className="h-3 w-3 shrink-0" />
                      <span>{event.timestamp ? new Date(event.timestamp).toLocaleString() : "N/A"}</span>
                      {event.evidence_id && (
                        <Badge variant="secondary" className="text-[9px]">Evidence</Badge>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </ScrollArea>
  );
}

function EventCard({
  event,
  isSelected,
  onSelect,
  compact,
}: {
  event: TimelineEvent;
  isSelected: boolean;
  onSelect: () => void;
  compact: boolean;
}) {
  return (
    <div
      className={`flex items-start gap-3 rounded-lg border p-2 transition-colors cursor-pointer ${
        isSelected ? "bg-primary/5 border-primary/20" : "hover:bg-muted/30"
      }`}
      onClick={onSelect}
    >
      <div className={`h-6 w-6 rounded-full flex items-center justify-center shrink-0 ${SOURCE_COLORS[event.source] ?? SOURCE_COLORS.system}`}>
        {(() => {
          const Icon = SOURCE_ICONS[event.source] ?? Clock;
          return <Icon className="h-3 w-3 text-foreground" />;
        })()}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-xs font-medium truncate">{event.title}</p>
          <Badge variant="outline" className="text-[9px] shrink-0">{event.source}</Badge>
        </div>
        {!compact && (
          <p className="text-[10px] text-muted-foreground mt-0.5 line-clamp-1">{event.description}</p>
        )}
        <div className="flex items-center gap-2 mt-0.5 text-[10px] text-muted-foreground">
          <Clock className="h-3 w-3 shrink-0" />
          <span>{event.timestamp ? new Date(event.timestamp).toLocaleString() : "N/A"}</span>
        </div>
      </div>
    </div>
  );
}
