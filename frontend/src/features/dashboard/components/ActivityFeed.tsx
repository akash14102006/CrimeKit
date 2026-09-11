"use client";

import { Activity, Briefcase, Upload, Brain, GitBranch } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCases } from "@/hooks/queries/useCases";
import { useAllEvidence } from "@/hooks/queries/useEvidence";
import { useQueueStats } from "@/hooks/queries/useStats";

interface FeedEvent {
  id: string;
  type: "case_created" | "evidence_uploaded" | "processing_started" | "ai_completed" | "kg_updated";
  title: string;
  description: string;
  timestamp: string;
}

function eventIcon(type: FeedEvent["type"]) {
  switch (type) {
    case "case_created":
      return <Briefcase className="h-4 w-4 text-primary" />;
    case "evidence_uploaded":
      return <Upload className="h-4 w-4 text-secondary-foreground" />;
    case "processing_started":
      return <Activity className="h-4 w-4 text-amber-500" />;
    case "ai_completed":
      return <Brain className="h-4 w-4 text-emerald-500" />;
    case "kg_updated":
      return <GitBranch className="h-4 w-4 text-blue-500" />;
  }
}

function FeedSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex items-start gap-3 p-2">
          <Skeleton className="h-8 w-8 rounded-full shrink-0" />
          <div className="space-y-1 flex-1">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-48" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>
      ))}
    </div>
  );
}

function useActivityFeed() {
  const { data: casesResponse, isLoading: casesLoading, error: casesError } = useCases({ page: 1, limit: 100 });
  const cases = casesResponse?.items;
  const { data: evidenceResponse, isLoading: evidenceLoading, error: evidenceError } = useAllEvidence({ page: 1, limit: 100 });
  const evidence = evidenceResponse?.items;
  const { data: queueStats, isLoading: queueLoading, error: queueError } = useQueueStats();

  const isLoading = casesLoading || evidenceLoading || queueLoading;
  const hasError = casesError || evidenceError || queueError;

  const events: FeedEvent[] = [];

  if (cases) {
    for (const c of cases.slice(0, 3)) {
      events.push({
        id: `case-${c.id}`,
        type: "case_created",
        title: `Case Created`,
        description: `"${c.title}" was opened`,
        timestamp: new Date().toISOString(),
      });
    }
  }

  if (evidence) {
    const sorted = evidence
      .slice()
      .sort((a, b) => {
        const da = a.uploaded_at ? new Date(a.uploaded_at).getTime() : 0;
        const db = b.uploaded_at ? new Date(b.uploaded_at).getTime() : 0;
        return db - da;
      })
      .slice(0, 3);

    for (const e of sorted) {
      events.push({
        id: `evidence-${e.id}`,
        type: "evidence_uploaded",
        title: "Evidence Uploaded",
        description: `"${e.filename}" was added to the evidence library`,
        timestamp: e.uploaded_at ?? new Date().toISOString(),
      });
    }
  }

  if (queueStats && queueStats.running > 0) {
    events.push({
      id: "processing-running",
      type: "processing_started",
      title: "Processing Active",
      description: `${queueStats.running} forensic job${queueStats.running !== 1 ? "s" : ""} currently running`,
      timestamp: new Date().toISOString(),
    });
  }

  events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return { events: events.slice(0, 8), isLoading, hasError };
}

export function ActivityFeed() {
  const { events, isLoading, hasError } = useActivityFeed();

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base">Activity Feed</CardTitle>
          <CardDescription>Recent system activity</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <FeedSkeleton />
        ) : hasError ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <Activity className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">Unable to load activity feed</p>
            <p className="text-xs text-muted-foreground/70 mt-1">Some data sources may be unavailable</p>
          </div>
        ) : events.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <Activity className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">No recent activity</p>
          </div>
        ) : (
          <div className="space-y-1">
            {events.map((event) => (
              <div
                key={event.id}
                className="flex items-start gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="mt-0.5 bg-muted p-1.5 rounded-full shrink-0">
                  {eventIcon(event.type)}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">{event.title}</p>
                  <p className="text-xs text-muted-foreground truncate">
                    {event.description}
                  </p>
                  <p className="text-xs text-muted-foreground/70 mt-0.5">
                    {new Date(event.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
