"use client";

import { useEffect, useRef, useCallback } from "react";
import { useGraphStore } from "../store/graphStore";
import { useAuthStore } from "@/store/authStore";
import { env } from "@/config/env";
import type { GraphNode, GraphEdge } from "@/types/kg";

interface GraphEvent {
  type: string;
  case_id: string;
  entity_name?: string;
  entity_type?: string;
  source_entity_id?: string;
  target_entity_id?: string;
  relationship?: string;
  evidence_id?: string;
  confidence?: number;
  metadata?: Record<string, unknown>;
  timestamp?: string;
}

const RECONNECT_DELAY = 1000;
const MAX_RECONNECT_DELAY = 30000;
const HEARTBEAT_INTERVAL = 25000;

export function useGraphWebSocket(caseId?: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectDelayRef = useRef(RECONNECT_DELAY);
  const mountedRef = useRef(true);
  const connectRef = useRef<(() => void) | null>(null);

  const {
    addNode,
    addEdge,
    setConnected,
    incrementPendingEvents,
    graphVersion,
  } = useGraphStore();

  const getAuthToken = useCallback(() => {
    const state = useAuthStore.getState();
    return state.sessionToken;
  }, []);

  const buildWsUrl = useCallback(
    (token: string) => {
      const base = env.apiBaseUrl || "http://localhost:8002";
      const protocol = base.startsWith("https") ? "wss" : "ws";
      const host = base.replace(/^https?:\/\//, "");
      return `${protocol}://${host}/ws/case/${caseId}?token=${token}`;
    },
    [caseId],
  );

  const handleEvent = useCallback(
    (event: GraphEvent) => {
      incrementPendingEvents();

      switch (event.type) {
        case "entity.detected": {
          if (event.entity_name && event.entity_type) {
            const node: GraphNode = {
              id: `${event.entity_type}:${event.entity_name}`,
              label: event.entity_name,
              type: event.entity_type,
              properties: {
                confidence: event.confidence,
                evidence_id: event.evidence_id,
                detected_at: event.timestamp,
                is_new: true,
              },
            };
            addNode(node);
          }
          break;
        }
        case "relationship.detected": {
          if (event.source_entity_id && event.target_entity_id && event.relationship) {
            const edge: GraphEdge = {
              id: `${event.source_entity_id}-${event.relationship}-${event.target_entity_id}`,
              source: event.source_entity_id,
              target: event.target_entity_id,
              type: event.relationship,
              label: event.relationship,
              properties: {
                confidence: event.confidence,
                evidence_id: event.evidence_id,
                detected_at: event.timestamp,
                is_new: true,
              },
            };
            addEdge(edge);
          }
          break;
        }
        case "graph.updated":
        case "evidence.processed": {
          break;
        }
      }
    },
    [addNode, addEdge, incrementPendingEvents],
  );

  const connect = useCallback(() => {
    if (!caseId || !mountedRef.current) return;

    const token = getAuthToken();
    if (!token) return;

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const url = buildWsUrl(token);
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setConnected(true);
      reconnectDelayRef.current = RECONNECT_DELAY;

      heartbeatIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "heartbeat" }));
        }
      }, HEARTBEAT_INTERVAL);
    };

    ws.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        if (data.type === "connected" || data.type === "pong") {
          return;
        }
        if (data.type === "sync" && data.events) {
          data.events.forEach((evt: GraphEvent) => handleEvent(evt));
          return;
        }
        handleEvent(data);
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = (event) => {
      setConnected(false);
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }

      if (mountedRef.current && event.code !== 1000) {
        const delay = reconnectDelayRef.current;
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectDelayRef.current = Math.min(
            reconnectDelayRef.current * 2,
            MAX_RECONNECT_DELAY,
          );
          connectRef.current?.();
        }, delay);
      }
    };

    ws.onerror = () => {};

    wsRef.current = ws;
  }, [caseId, getAuthToken, buildWsUrl, setConnected, handleEvent]);

  // Keep ref in sync with latest connect
  useEffect(() => {
    connectRef.current = connect;
  });

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, "Component unmounted");
        wsRef.current = null;
      }
    };
  }, [caseId, connect]);

  const requestSync = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN && graphVersion) {
      wsRef.current.send(
        JSON.stringify({
          type: "request_sync",
          last_timestamp: graphVersion / 1000,
        }),
      );
    }
  }, [graphVersion]);

  return {
    isConnected: useGraphStore((s) => s.isConnected),
    pendingEvents: useGraphStore((s) => s.pendingEvents),
    requestSync,
  };
}
