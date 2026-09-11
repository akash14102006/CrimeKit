"use client";

import { useMemo } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Clock,
  Shield,
  Activity,
} from "lucide-react";
import { useWorkspace, useWorkspaceCustody } from "@/hooks/queries/useWorkspace";
import { useWorkspaceStore } from "@/store/workspaceStore";

interface Props {
  caseId: string;
}

const TIMELINE_ICONS: Record<string, typeof Clock> = {
  upload: Clock,
  evidence: Clock,
  processing: Activity,
  ai: Activity,
  custody: Shield,
  system: Activity,
};

function TimelineTab({ caseId }: { caseId: string }) {
  const { data: workspace, isLoading } = useWorkspace(caseId);

  const events = useMemo(() => {
    return workspace?.timeline ?? [];
  }, [workspace]);

  if (isLoading) {
    return (
      <div className="space-y-3 p-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="h-8 w-8 rounded-full shrink-0" />
            <div className="flex-1 space-y-1">
              <Skeleton className="h-4 w-[150px]" />
              <Skeleton className="h-3 w-[200px]" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!events.length) {
    return (
      <div className="text-center py-6">
        <Clock className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
        <p className="text-xs text-muted-foreground">No timeline events yet</p>
        <p className="text-[10px] text-muted-foreground mt-1">Events will appear as evidence is processed and investigated</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 p-3">
      {events.map((event, i) => {
        const Icon = TIMELINE_ICONS[event.source_type] ?? Clock;
        return (
          <div key={i} className="flex gap-3 items-start">
            <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center shrink-0 mt-0.5">
              <Icon className="h-3.5 w-3.5 text-muted-foreground" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium">{event.summary}</p>
              <div className="flex items-center gap-2 text-[10px] text-muted-foreground mt-0.5">
                {event.timestamp && <span>{new Date(event.timestamp).toLocaleString()}</span>}
                {event.date && <span>{event.date}</span>}
                <Badge variant="outline" className="text-[10px]">{event.source_type}</Badge>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CustodyTab({ caseId }: Props) {
  const { data: custody, isLoading } = useWorkspaceCustody(caseId);

  if (isLoading) {
    return (
      <div className="space-y-3 p-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="h-7 w-7 rounded-full shrink-0" />
            <div className="flex-1 space-y-1">
              <Skeleton className="h-4 w-[150px]" />
              <Skeleton className="h-3 w-[200px]" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!custody || custody.length === 0) {
    return (
      <div className="text-center py-6">
        <Shield className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
        <p className="text-xs text-muted-foreground">No custody events yet</p>
        <p className="text-[10px] text-muted-foreground mt-1">Chain of custody will be recorded as evidence is handled</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 p-3">
      {custody.map((event, i) => (
        <div key={i} className="flex gap-3 items-start">
          <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center shrink-0 mt-0.5">
            <Shield className="h-3.5 w-3.5 text-muted-foreground" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium">{event.action}</p>
            <div className="flex items-center gap-2 text-[10px] text-muted-foreground mt-0.5">
              {event.timestamp && <span>{new Date(event.timestamp).toLocaleString()}</span>}
              {event.actor_id && <span>by {event.actor_id.slice(0, 8)}...</span>}
            </div>
            {event.notes && (
              <p className="text-[10px] text-muted-foreground mt-1 italic">{event.notes}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function ActivityTab({ caseId }: Props) {
  const { data: workspace, isLoading } = useWorkspace(caseId);

  if (isLoading) {
    return (
      <div className="space-y-3 p-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    );
  }

  const evidenceCount = workspace?.evidence?.length ?? 0;
  const custodyCount = workspace?.custody?.length ?? 0;
  const timelineCount = workspace?.timeline?.length ?? 0;
  const findingsCount = workspace?.ai_findings?.length ?? 0;

  return (
    <div className="space-y-3 p-3">
      <h4 className="text-xs font-semibold flex items-center gap-1.5">
        <Activity className="h-3.5 w-3.5" />
        Activity Summary
      </h4>
      <div className="grid grid-cols-2 gap-2 text-center">
        <div className="p-2 rounded bg-muted/50">
          <p className="font-medium text-foreground">{evidenceCount}</p>
          <p className="text-[10px] text-muted-foreground">Evidence Items</p>
        </div>
        <div className="p-2 rounded bg-muted/50">
          <p className="font-medium text-foreground">{custodyCount}</p>
          <p className="text-[10px] text-muted-foreground">Custody Events</p>
        </div>
        <div className="p-2 rounded bg-muted/50">
          <p className="font-medium text-foreground">{timelineCount}</p>
          <p className="text-[10px] text-muted-foreground">Timeline Events</p>
        </div>
        <div className="p-2 rounded bg-muted/50">
          <p className="font-medium text-foreground">{findingsCount}</p>
          <p className="text-[10px] text-muted-foreground">AI Findings</p>
        </div>
      </div>
      {workspace?.progress && (
        <div className="space-y-1 text-xs">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Overall Progress</span>
            <span className="font-medium">{workspace.progress.completion_percent}%</span>
          </div>
          <div className="h-1 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all"
              style={{ width: `${workspace.progress.completion_percent}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export function BottomPanel({ caseId }: Props) {
  const { activeBottomTab, setActiveBottomTab } = useWorkspaceStore();

  return (
    <div className="flex h-full flex-col">
      <Tabs
        value={activeBottomTab}
        onValueChange={(v) => setActiveBottomTab(v as "timeline" | "custody" | "activity")}
        className="flex h-full flex-col"
      >
        <TabsList className="grid w-full grid-cols-3 h-9 mx-2 mt-2 w-[calc(100%-16px)]">
          <TabsTrigger value="timeline" className="text-[10px] gap-1">
            <Clock className="h-3 w-3" />
            Timeline
          </TabsTrigger>
          <TabsTrigger value="custody" className="text-[10px] gap-1">
            <Shield className="h-3 w-3" />
            Custody
          </TabsTrigger>
          <TabsTrigger value="activity" className="text-[10px] gap-1">
            <Activity className="h-3 w-3" />
            Activity
          </TabsTrigger>
        </TabsList>

        <TabsContent value="timeline" className="flex-1 overflow-hidden mt-0">
          <ScrollArea className="h-full">
            <TimelineTab caseId={caseId} />
          </ScrollArea>
        </TabsContent>

        <TabsContent value="custody" className="flex-1 overflow-hidden mt-0">
          <ScrollArea className="h-full">
            <CustodyTab caseId={caseId} />
          </ScrollArea>
        </TabsContent>

        <TabsContent value="activity" className="flex-1 overflow-hidden mt-0">
          <ScrollArea className="h-full">
            <ActivityTab caseId={caseId} />
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}
