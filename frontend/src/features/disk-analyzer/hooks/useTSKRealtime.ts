"use client";

import { useEffect, useRef } from "react";
import { env } from "@/config/env";
import { useAuthStore } from "@/store/authStore";
import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";
import type { TSKProcessingStage } from "@/types/tsk";

interface TSKEvent {
  type?: string;
  event_type?: string;
  stage?: string;
  data?: {
    progress_percent?: number;
    progress?: number;
    error?: string;
  };
}

export function useTSKRealtime(caseId: string | null, evidenceId: string) {
  const socketRef = useRef<WebSocket | null>(null);
  const setProcessingStage = useDiskAnalyzerStore((state) => state.setProcessingStage);
  const setProgressPercent = useDiskAnalyzerStore((state) => state.setProgressPercent);
  const setStagesCompleted = useDiskAnalyzerStore((state) => state.setStagesCompleted);
  const setStagesFailed = useDiskAnalyzerStore((state) => state.setStagesFailed);
  const setErrors = useDiskAnalyzerStore((state) => state.setErrors);

  useEffect(() => {
    const token = useAuthStore.getState().sessionToken;
    if (!caseId || !evidenceId || !token) return;

    const base = env.apiBaseUrl || "http://localhost:8002";
    const protocol = base.startsWith("https") ? "wss" : "ws";
    const host = base.replace(/^https?:\/\//, "");
    const socket = new WebSocket(`${protocol}://${host}/ws/case/${caseId}?token=${token}`);
    socketRef.current = socket;

    socket.onmessage = (message) => {
      try {
        const event = JSON.parse(message.data) as TSKEvent & { evidence_id?: string };
        if (event.evidence_id !== evidenceId || !event.stage && !event.event_type?.startsWith("forensic.")) return;
        const stage = event.stage as TSKProcessingStage | undefined;
        const eventType = event.event_type ?? event.type ?? "";
        if (stage) {
          setProcessingStage(stage);
          if (eventType.endsWith(".completed")) {
            const current = useDiskAnalyzerStore.getState().stagesCompleted;
            setStagesCompleted([...new Set([...current, stage])]);
          }
          if (eventType.endsWith(".failed")) {
            setStagesFailed([...new Set([...useDiskAnalyzerStore.getState().stagesFailed, stage])]);
            if (event.data?.error) setErrors([event.data.error]);
          }
        }
        const progress = event.data?.progress_percent ?? event.data?.progress;
        if (typeof progress === "number") setProgressPercent(progress);
      } catch {
        // Ignore unrelated messages on the shared case channel.
      }
    };

    return () => {
      socket.close(1000, "Analyzer closed");
      socketRef.current = null;
    };
  }, [caseId, evidenceId, setErrors, setProcessingStage, setProgressPercent, setStagesCompleted, setStagesFailed]);
}
