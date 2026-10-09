"use client";

import { useEffect, useRef, useCallback } from "react";
import { useAuthStore } from "@/store/authStore";
import { env } from "@/config/env";
import { useLiveInvestigationStore } from "../store/liveInvestigationStore";

export function useLiveInvestigationWebSocket(caseId?: string) {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isIntentionalCloseRef = useRef(false);

  const {
    connectionStatus,
    setConnectionStatus,
    ingestLiveEvent,
  } = useLiveInvestigationStore();

  const getAuthToken = useCallback(() => {
    return useAuthStore.getState().sessionToken;
  }, []);

  const buildWsUrl = useCallback(
    (token: string, targetCaseId: string) => {
      const base = env.apiBaseUrl;
      const protocol = base.startsWith("https") ? "wss" : "ws";
      const host = base.replace(/^https?:\/\//, "");
      return `${protocol}://${host}/ws/case/${targetCaseId}?token=${token}`;
    },
    [],
  );

  const connect = useCallback(() => {
    if (!caseId) return;

    const token = getAuthToken();
    if (!token) {
      setConnectionStatus("DISCONNECTED");
      return;
    }

    if (socketRef.current && (socketRef.current.readyState === WebSocket.OPEN || socketRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      const wsUrl = buildWsUrl(token, caseId);
      setConnectionStatus("CONNECTING");

      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setConnectionStatus("CONNECTED");
        isIntentionalCloseRef.current = false;

        // Keepalive ping interval
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "ping" }));
          }
        }, 25000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Ignore pong heartbeats in domain store
          if (data.type === "pong" || data.type === "connected") {
            return;
          }
          // Ingest investigation domain events
          ingestLiveEvent(data);
        } catch {
          // ignore non-json frames
        }
      };

      ws.onerror = () => {
        setConnectionStatus("ERROR");
      };

      ws.onclose = () => {
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        if (!isIntentionalCloseRef.current) {
          setConnectionStatus("RECONNECTING");
          // Reconnect with 3s backoff
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        } else {
          setConnectionStatus("DISCONNECTED");
        }
      };
    } catch {
      setConnectionStatus("ERROR");
    }
  }, [caseId, getAuthToken, buildWsUrl, setConnectionStatus, ingestLiveEvent]);

  useEffect(() => {
    if (!caseId) return;
    isIntentionalCloseRef.current = false;
    connect();

    return () => {
      isIntentionalCloseRef.current = true;
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [caseId, connect]);

  return {
    connectionStatus,
    reconnect: connect,
  };
}
