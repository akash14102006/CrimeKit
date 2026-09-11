"use client";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Cpu,
  Circle,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
} from "lucide-react";
import { useQueueStats } from "@/hooks/queries/useStats";
import { useWorkspaceProgress } from "@/hooks/queries/useWorkspace";

interface AgentInfo {
  name: string;
  description: string;
  icon: string;
  status: "idle" | "running" | "queued" | "completed" | "failed";
}

const KNOWN_AGENTS: Omit<AgentInfo, "status">[] = [
  { name: "Supervisor", description: "Task orchestration & routing", icon: "🧠" },
  { name: "Detective", description: "Entity extraction & analysis", icon: "🔍" },
  { name: "Correlation", description: "Cross-entity relationship discovery", icon: "🔗" },
  { name: "Timeline", description: "Temporal event extraction", icon: "📅" },
  { name: "Evidence", description: "Evidence processing & analysis", icon: "📄" },
  { name: "Knowledge Graph", description: "Graph construction & queries", icon: "🕸️" },
  { name: "Report", description: "Report generation & formatting", icon: "📋" },
  { name: "Search", description: "Full-text & semantic search", icon: "🔎" },
  { name: "OCR", description: "Optical character recognition", icon: "👁️" },
  { name: "Forensic", description: "Deep forensic analysis", icon: "🔬" },
  { name: "RAG", description: "Retrieval-augmented generation", icon: "📚" },
  { name: "Embedding", description: "Vector embedding generation", icon: "🔢" },
];

function StatusIcon({ status }: { status: AgentInfo["status"] }) {
  switch (status) {
    case "running":
      return <Loader2 className="h-3 w-3 text-blue-500 animate-spin" />;
    case "queued":
      return <Clock className="h-3 w-3 text-amber-500" />;
    case "completed":
      return <CheckCircle className="h-3 w-3 text-green-500" />;
    case "failed":
      return <XCircle className="h-3 w-3 text-red-500" />;
    default:
      return <Circle className="h-3 w-3 text-muted-foreground" />;
  }
}

function StatusBadge({ status }: { status: AgentInfo["status"] }) {
  const variants: Record<string, string> = {
    idle: "bg-gray-100 text-gray-700",
    running: "bg-blue-100 text-blue-700",
    queued: "bg-amber-100 text-amber-700",
    completed: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
  };

  return (
    <Badge variant="outline" className={`text-[10px] ${variants[status]}`}>
      {status}
    </Badge>
  );
}

export function AgentStatusPanel({ caseId: _caseId }: { caseId: string }) {
  const { data: queueStats, isLoading: statsLoading } = useQueueStats();
  const { data: progress, isLoading: progressLoading } = useWorkspaceProgress(
    _caseId,
  );

  const isLoading = statsLoading || progressLoading;

  const agents: AgentInfo[] = KNOWN_AGENTS.map((agent) => {
    let status: AgentInfo["status"] = "idle";

    if (queueStats) {
      if (queueStats.running > 0 && agent.name === "Forensic") {
        status = "running";
      } else if (queueStats.queued > 0 && agent.name === "Evidence") {
        status = "queued";
      }
    }

    if (progress) {
      if (progress.forensic_jobs_completed > 0 && agent.name === "Supervisor") {
        status = "completed";
      }
      if (progress.forensic_jobs_failed > 0 && agent.name === "Forensic") {
        status = "failed";
      }
    }

    return { ...agent, status };
  });

  const runningCount = agents.filter((a) => a.status === "running").length;
  const completedCount = agents.filter((a) => a.status === "completed").length;
  const failedCount = agents.filter((a) => a.status === "failed").length;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-semibold">Agent Status</h3>
        </div>
        <div className="flex items-center gap-2">
          {runningCount > 0 && (
            <Badge variant="secondary" className="text-[10px] gap-1">
              <Loader2 className="h-2.5 w-2.5 animate-spin" />
              {runningCount} running
            </Badge>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="p-4 space-y-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </div>
      ) : (
        <ScrollArea className="flex-1">
          <div className="p-4 space-y-2">
            {queueStats && (
              <div className="grid grid-cols-4 gap-2 mb-4">
                <div className="text-center p-2 rounded bg-muted/50">
                  <div className="text-lg font-bold">{queueStats.queued}</div>
                  <div className="text-[10px] text-muted-foreground">Queued</div>
                </div>
                <div className="text-center p-2 rounded bg-blue-50">
                  <div className="text-lg font-bold text-blue-600">
                    {queueStats.running}
                  </div>
                  <div className="text-[10px] text-muted-foreground">Running</div>
                </div>
                <div className="text-center p-2 rounded bg-green-50">
                  <div className="text-lg font-bold text-green-600">
                    {completedCount}
                  </div>
                  <div className="text-[10px] text-muted-foreground">Done</div>
                </div>
                <div className="text-center p-2 rounded bg-red-50">
                  <div className="text-lg font-bold text-red-600">
                    {failedCount}
                  </div>
                  <div className="text-[10px] text-muted-foreground">Failed</div>
                </div>
              </div>
            )}

            {agents.map((agent) => (
              <div
                key={agent.name}
                className="flex items-center gap-3 p-2 rounded-md hover:bg-muted/30 transition-colors"
              >
                <span className="text-lg">{agent.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{agent.name}</span>
                    <StatusIcon status={agent.status} />
                  </div>
                  <p className="text-[10px] text-muted-foreground truncate">
                    {agent.description}
                  </p>
                </div>
                <StatusBadge status={agent.status} />
              </div>
            ))}
          </div>
        </ScrollArea>
      )}
    </div>
  );
}
