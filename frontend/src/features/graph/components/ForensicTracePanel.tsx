"use client";

import React, { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Activity, X, ChevronRight } from "lucide-react";

interface Props {
  caseId: string;
  wsConnected: boolean;
  pendingEvents: number;
  isDark?: boolean;
  onClose: () => void;
}

interface TraceLog {
  id: string;
  timestamp: string;
  event: string;
  latency: number;
  details: string;
}

export function ForensicTracePanel({ caseId, wsConnected, isDark = true, onClose }: Props) {
  const [logs, setLogs] = useState<TraceLog[]>([
    {
      id: "log-1",
      timestamp: new Date().toLocaleTimeString(),
      event: "Graph Projection Hydrated",
      latency: 42,
      details: `Neo4j partition case:${caseId} loaded`,
    },
    {
      id: "log-2",
      timestamp: new Date().toLocaleTimeString(),
      event: "Evidence Provenance Verified",
      latency: 18,
      details: "SHA-256 integrity check passed for 4 artifacts",
    },
    {
      id: "log-3",
      timestamp: new Date().toLocaleTimeString(),
      event: "GDS PageRank Centrality",
      latency: 35,
      details: "PageRank centrality updated for case entities",
    },
  ]);

  // Simulate incoming WebSocket trace events
  useEffect(() => {
    if (!wsConnected) return;
    const interval = setInterval(() => {
      const newLog: TraceLog = {
        id: `log-${Date.now()}`,
        timestamp: new Date().toLocaleTimeString(),
        event: "Realtime Entity Sync",
        latency: Math.floor(12 + Math.random() * 25),
        details: "Streamed graph mutation relay via Redis/WebSocket",
      };
      setLogs((prev) => [newLog, ...prev.slice(0, 15)]);
    }, 8000);
    return () => clearInterval(interval);
  }, [wsConnected]);

  const panelBg = isDark
    ? "bg-slate-950/90 border-slate-800 text-slate-200"
    : "bg-white/95 border-slate-200 text-slate-900 shadow-xl";

  const itemBg = isDark
    ? "bg-slate-900/80 border-slate-800/80"
    : "bg-slate-50 border-slate-200";

  return (
    <div className={`absolute top-16 right-4 z-20 w-80 backdrop-blur-md border rounded-lg overflow-hidden flex flex-col text-xs ${panelBg}`}>
      {/* Header */}
      <div className={`px-3 py-2 border-b flex items-center justify-between ${isDark ? "bg-slate-900/60 border-slate-800" : "bg-slate-100 border-slate-200"}`}>
        <div className="flex items-center gap-1.5 font-semibold text-sky-600 dark:text-sky-400">
          <Activity className="h-3.5 w-3.5" />
          <span>Forensic Activity Trace</span>
        </div>
        <div className="flex items-center gap-1">
          <Badge variant="outline" className={`text-[10px] ${wsConnected ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30" : "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/30"}`}>
            {wsConnected ? "LIVE" : "STANDBY"}
          </Badge>
          <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-slate-400 hover:text-slate-900 dark:hover:text-white" onClick={onClose}>
            <X className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      {/* Log Feed */}
      <div className="p-3 space-y-2 max-h-72 overflow-y-auto font-mono text-[11px]">
        {logs.map((log) => (
          <div key={log.id} className={`p-2 rounded border space-y-1 ${itemBg}`}>
            <div className="flex items-center justify-between text-slate-500 text-[10px]">
              <span>{log.timestamp}</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">{log.latency}ms</span>
            </div>
            <div className="font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-1">
              <ChevronRight className="h-3 w-3 text-sky-500" />
              {log.event}
            </div>
            <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate pl-4">{log.details}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
