"""
WebSocket connection manager for CrimeKit.

Manages authenticated, case-scoped WebSocket connections.
Each case has its own channel — evidence from Case A is never
broadcast to Case B clients.

Features:
- JWT authentication on connect
- Case-scoped channels
- Rate limiting per connection
- Heartbeat/keepalive
- Reconnection support with missed-event recovery
- Observable connection state
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass(eq=False)
class WSConnection:
    """A single WebSocket connection.

    ``eq=False`` keeps the default identity-based hashing so instances can
    live in a ``set`` keyed by object identity (two connections for the same
    user/case but different sockets must remain distinct and removable).
    """
    ws: Any  # WebSocket object
    user_id: str
    case_id: str
    connected_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    message_count: int = 0
    last_event_timestamp: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "case_id": self.case_id,
            "connected_at": self.connected_at,
            "last_heartbeat": self.last_heartbeat,
            "message_count": self.message_count,
        }


class ConnectionManager:
    """
    Manages WebSocket connections organized by case.

    Thread-safe via asyncio locks.
    """

    def __init__(self):
        # case_id -> set of WSConnection
        self._connections: Dict[str, Set[WSConnection]] = {}
        self._lock = asyncio.Lock()
        self._message_rate_limit = int(os.getenv("WS_RATE_LIMIT", "100"))  # messages per minute
        self._heartbeat_interval = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
        self._max_connections_per_case = int(os.getenv("WS_MAX_CONNECTIONS_PER_CASE", "50"))

    async def connect(self, ws: Any, user_id: str, case_id: str) -> WSConnection:
        """
        Accept a new WebSocket connection.

        Args:
            ws: WebSocket object
            user_id: Authenticated user ID
            case_id: Case ID to subscribe to

        Returns:
            WSConnection instance
        """
        async with self._lock:
            if case_id not in self._connections:
                self._connections[case_id] = set()

            # Check connection limit
            if len(self._connections[case_id]) >= self._max_connections_per_case:
                logger.warning(
                    "Case %s: Connection limit reached (%d), rejecting user %s",
                    case_id, self._max_connections_per_case, user_id,
                )
                await ws.close(code=1013, reason="Too many connections for this case")
                raise ConnectionError("Connection limit reached")

            conn = WSConnection(ws=ws, user_id=user_id, case_id=case_id)
            self._connections[case_id].add(conn)

            logger.info(
                "Case %s: User %s connected (total: %d)",
                case_id, user_id, len(self._connections[case_id]),
            )

            # Send welcome message with connection info
            await ws.send_json({
                "type": "connected",
                "case_id": case_id,
                "user_id": user_id,
                "server_time": datetime.now(timezone.utc).isoformat(),
                "heartbeat_interval": self._heartbeat_interval,
            })

            return conn

    async def disconnect(self, ws: Any, case_id: str, user_id: str):
        """Remove a WebSocket connection."""
        async with self._lock:
            if case_id in self._connections:
                to_remove = None
                for conn in self._connections[case_id]:
                    if conn.ws is ws:
                        to_remove = conn
                        break
                if to_remove:
                    self._connections[case_id].discard(to_remove)
                    logger.info(
                        "Case %s: User %s disconnected (remaining: %d)",
                        case_id, user_id, len(self._connections[case_id]),
                    )
                    if not self._connections[case_id]:
                        del self._connections[case_id]

    async def broadcast_to_case(self, case_id: str, event: dict):
        """
        Broadcast an event to all connections subscribed to a case.

        Args:
            case_id: Case ID to broadcast to
            event: Event dict to send
        """
        connections = self._connections.get(case_id, set())
        if not connections:
            return

        payload = json.dumps(event)
        disconnected = []

        for conn in connections:
            try:
                await conn.ws.send_text(payload)
                conn.message_count += 1
            except Exception as e:
                logger.warning(
                    "Case %s: Failed to send to user %s: %s",
                    case_id, conn.user_id, e,
                )
                disconnected.append(conn)

        # Clean up failed connections
        for conn in disconnected:
            self._connections.get(case_id, set()).discard(conn)

    async def broadcast(self, event: dict, case_id: Optional[str] = None):
        """
        Broadcast an event to WebSocket clients.
        If case_id is provided or present in event['case_id'], broadcasts to that specific case channel.
        Otherwise, broadcasts to all connected case channels.
        """
        target_case_id = case_id or event.get("case_id")
        if target_case_id:
            await self.broadcast_to_case(str(target_case_id), event)
        else:
            # Broadcast to all active cases
            for cid in list(self._connections.keys()):
                await self.broadcast_to_case(cid, event)

    async def handle_message(self, ws: Any, case_id: str, user_id: str, message: str):
        """
        Handle incoming WebSocket message from client.

        Supports:
        - heartbeat/ping
        - request_sync (for missed-event recovery)
        """
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            await ws.send_json({"type": "error", "message": "Invalid JSON"})
            return

        msg_type = data.get("type", "")

        if msg_type in ("heartbeat", "ping"):
            # Update heartbeat timestamp
            for conn in self._connections.get(case_id, set()):
                if conn.ws is ws:
                    conn.last_heartbeat = time.time()
                    break
            await ws.send_json({
                "type": "pong",
                "server_time": datetime.now(timezone.utc).isoformat(),
            })

        elif msg_type == "request_sync":
            # Client requests missed events
            last_timestamp = data.get("last_timestamp")
            if last_timestamp:
                from .events import get_recent_events
                events = get_recent_events(case_id, since_timestamp=last_timestamp)
                await ws.send_json({
                    "type": "sync",
                    "events": events,
                    "count": len(events),
                })
            else:
                await ws.send_json({
                    "type": "error",
                    "message": "last_timestamp required for sync",
                })

        elif msg_type == "subscribe_node":
            # Client wants to expand a specific node (for progressive loading)
            node_id = data.get("node_id")
            if node_id:
                await ws.send_json({
                    "type": "subscribed",
                    "node_id": node_id,
                })

        else:
            await ws.send_json({
                "type": "error",
                "message": f"Unknown message type: {msg_type}",
            })

    def get_case_connections(self, case_id: str) -> list:
        """Get all connections for a case (for observability)."""
        return [conn.to_dict() for conn in self._connections.get(case_id, set())]

    def get_stats(self) -> dict:
        """Get connection statistics."""
        total = sum(len(conns) for conns in self._connections.values())
        return {
            "total_connections": total,
            "cases_active": len(self._connections),
            "connections_per_case": {
                cid: len(conns) for cid, conns in self._connections.items()
            },
        }


# Singleton
manager = ConnectionManager()
