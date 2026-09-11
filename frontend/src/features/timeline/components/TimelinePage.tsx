"use client";

import { useEffect, useMemo, useCallback } from "react";
import { useParams } from "next/navigation";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { useTimeline } from "@/hooks/queries/useTimeline";
import { useCaseTimeline } from "@/hooks/queries/useTimeline";
import { useTimelineStore } from "../store/timelineStore";
import { TimelineToolbar } from "./TimelineToolbar";
import { TimelineView } from "./TimelineView";
import { TimelineEventDetail } from "./TimelineEventDetail";
import { TimelineLegend } from "./TimelineLegend";

interface Props {
  caseId?: string;
}

export function TimelinePage({ caseId: propCaseId }: Props = {}) {
  const params = useParams();
  const caseId = propCaseId ?? (params?.caseId as string);

  const { setCaseId } = useTimelineStore();

  useEffect(() => {
    setCaseId(caseId ?? null);
  }, [caseId, setCaseId]);

  const { data: globalTimeline, isLoading: globalLoading, refetch: refetchGlobal } = useTimeline({ limit: 500 });
  const { data: caseTimeline, isLoading: caseLoading, refetch: refetchCase } = useCaseTimeline(caseId);

  const rawEvents = useMemo(() => {
    if (caseId) return caseTimeline ?? [];
    return globalTimeline ?? [];
  }, [caseId, caseTimeline, globalTimeline]);

  const isLoading = caseId ? caseLoading : globalLoading;
  const refetch = caseId ? refetchCase : refetchGlobal;

  const {
    searchQuery,
    sourceFilter,
    dateFrom,
    dateTo,
    selectedEventId,
    selectEvent,
  } = useTimelineStore();

  const filteredEvents = useMemo(() => {
    let events = rawEvents;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      events = events.filter(
        (e) =>
          e.title.toLowerCase().includes(q) ||
          e.description.toLowerCase().includes(q) ||
          e.source.toLowerCase().includes(q) ||
          e.evidence_id?.toLowerCase().includes(q) ||
          e.id.toLowerCase().includes(q),
      );
    }

    if (sourceFilter && sourceFilter !== "all") {
      events = events.filter((e) => e.source === sourceFilter);
    }

    if (dateFrom) {
      const from = new Date(dateFrom).getTime();
      events = events.filter((e) => new Date(e.timestamp).getTime() >= from);
    }

    if (dateTo) {
      const to = new Date(dateTo).getTime();
      events = events.filter((e) => new Date(e.timestamp).getTime() <= to);
    }

    return events;
  }, [rawEvents, searchQuery, sourceFilter, dateFrom, dateTo]);

  const selectedEvent = useMemo(
    () => filteredEvents.find((e) => e.id === selectedEventId) ?? null,
    [filteredEvents, selectedEventId],
  );

  const selectedIndex = useMemo(
    () => filteredEvents.findIndex((e) => e.id === selectedEventId),
    [filteredEvents, selectedEventId],
  );

  const handleNavigate = useCallback(
    (direction: "prev" | "next") => {
      if (selectedIndex < 0) return;
      const nextIndex = direction === "next" ? selectedIndex + 1 : selectedIndex - 1;
      if (nextIndex >= 0 && nextIndex < filteredEvents.length) {
        selectEvent(filteredEvents[nextIndex].id);
      }
    },
    [selectedIndex, filteredEvents, selectEvent],
  );

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Investigation Timeline</h1>
          <p className="text-sm text-muted-foreground">
            {caseId ? `Case-scoped chronological view` : `Global chronological view`}
          </p>
        </div>
      </div>

      <div className="px-4 py-2 border-b">
        <TimelineToolbar events={filteredEvents} isLoading={isLoading} onRefresh={() => refetch()} />
      </div>

      <div className="px-4 py-1.5 border-b">
        <TimelineLegend />
      </div>

      <div className="flex-1 min-h-0">
        <ResizablePanelGroup orientation="horizontal" className="h-full">
          <ResizablePanel defaultSize={selectedEvent ? 60 : 100} minSize={40}>
            <TimelineView events={filteredEvents} isLoading={isLoading} />
          </ResizablePanel>
          {selectedEvent && (
            <>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={40} minSize={30} collapsible collapsedSize={0}>
                <TimelineEventDetail
                  event={selectedEvent}
                  onClose={() => selectEvent(null)}
                  onNavigate={handleNavigate}
                  hasPrev={selectedIndex > 0}
                  hasNext={selectedIndex < filteredEvents.length - 1}
                />
              </ResizablePanel>
            </>
          )}
        </ResizablePanelGroup>
      </div>
    </div>
  );
}
