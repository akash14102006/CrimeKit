"use client";

import { Suspense, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Loader2,
  Activity,
  Server,
  Clock,
  CheckCircle2,
  XCircle,
  History,
  BarChart3,
  RefreshCw,
  Search,
  Filter,
  AlertTriangle,
} from "lucide-react";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { QueueOverviewCards } from "../components/QueueOverviewCards";
import { WorkerStatusPanel } from "../components/WorkerStatusPanel";
import { LiveJobs } from "../components/LiveJobs";
import { ProcessingPipeline } from "../components/ProcessingPipeline";
import { JobDetailsDrawer } from "../components/JobDetailsDrawer";
import { FailedJobs } from "../components/FailedJobs";
import { ProcessingHistory } from "../components/ProcessingHistory";
import { ProcessingLogs } from "../components/ProcessingLogs";
import { QueueAnalytics } from "../components/QueueAnalytics";
import { useProcessingOverview } from "../hooks/useProcessing";
import { useProcessingStore, type ProcessingTab } from "../store/processingStore";

function ProcessingContent() {
  const overview = useProcessingOverview();
  const { activeTab, setActiveTab, drawerOpen } = useProcessingStore();

  const tabs: { key: ProcessingTab; label: string; icon: React.ReactNode; count?: number }[] = [
    { key: "overview", label: "Overview", icon: <Activity className="h-3 w-3" /> },
    { key: "running", label: "Running", icon: <Clock className="h-3 w-3" />, count: overview.queueStats?.running },
    { key: "completed", label: "Completed", icon: <CheckCircle2 className="h-3 w-3" />, count: overview.queueStats?.completed },
    { key: "failed", label: "Failed", icon: <XCircle className="h-3 w-3" />, count: overview.queueStats?.failed },
    { key: "workers", label: "Workers", icon: <Server className="h-3 w-3" />, count: overview.workers.length },
    { key: "history", label: "History", icon: <History className="h-3 w-3" /> },
    { key: "dlq", label: "DLQ", icon: <AlertTriangle className="h-3 w-3" /> },
    { key: "analytics", label: "Analytics", icon: <BarChart3 className="h-3 w-3" /> },
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="px-6 py-4 border-b space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="h-5 w-5 text-primary" />
              <h1 className="text-lg font-semibold">Processing Queue</h1>
              {overview.queueStats && (
                <Badge variant="secondary" className="text-[10px]">
                  {overview.queueStats.queued + overview.queueStats.running} active
                </Badge>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 text-xs gap-1"
              onClick={() => overview.refetch()}
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Refresh All
            </Button>
          </div>

          <QueueOverviewCards />

          <div className="flex items-center gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-xs transition-colors ${
                  activeTab === tab.key
                    ? "bg-muted font-medium"
                    : "text-muted-foreground hover:bg-muted/50"
                }`}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.icon}
                {tab.label}
                {tab.count !== undefined && tab.count > 0 && (
                  <Badge variant="secondary" className="text-[8px] ml-0.5">
                    {tab.count}
                  </Badge>
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 flex min-h-0">
          <div className="flex-1 overflow-auto">
            {activeTab === "overview" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <WorkerStatusPanel />
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <LiveJobs />
                    <FailedJobs />
                  </div>
                  <QueueAnalytics />
                </div>
              </ScrollArea>
            )}

            {activeTab === "running" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <LiveJobs />
                  <ProcessingPipeline />
                </div>
              </ScrollArea>
            )}

            {activeTab === "completed" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <ProcessingHistory />
                </div>
              </ScrollArea>
            )}

            {activeTab === "failed" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <FailedJobs />
                  <ProcessingLogs />
                </div>
              </ScrollArea>
            )}

            {activeTab === "workers" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <WorkerStatusPanel />
                </div>
              </ScrollArea>
            )}

            {activeTab === "history" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <ProcessingHistory />
                  <ProcessingLogs />
                </div>
              </ScrollArea>
            )}

            {activeTab === "dlq" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <FailedJobs />
                </div>
              </ScrollArea>
            )}

            {activeTab === "analytics" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <QueueAnalytics />
                  <ProcessingHistory />
                </div>
              </ScrollArea>
            )}
          </div>

          {drawerOpen && <JobDetailsDrawer />}
        </div>
      </div>
    </div>
  );
}

export default function ProcessingPage() {
  return (
    <AuthGuard
      allowedRoles={["admin", "investigator", "analyst"]}
    >
      <Suspense
        fallback={
          <div className="flex h-[400px] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        }
      >
        <ProcessingContent />
      </Suspense>
    </AuthGuard>
  );
}
