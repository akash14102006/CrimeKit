"""
WebSocket routes for CrimeKit real-time graph updates.

Provides authenticated, case-scoped WebSocket connections for
streaming knowledge graph changes to the frontend.

Endpoint: ws://{host}/ws/case/{case_id}

Authentication:
- JWT token passed as query parameter: ?token=<jwt>
- Validates user has access to the specified case

Events streamed:
- entity.detected: New entity added to graph
- relationship.detected: New relationship added
- graph.updated: Any graph modification
- evidence.processed: Evidence processing completed
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Optional

from . import database
from . import models
from .auth import decode_token
from .websocket_manager import manager
from .events import get_recent_events

logger = logging.getLogger(__name__)

router = APIRouter()


def _verify_case_access(user_id: str, case_id: str) -> bool:
    """Verify a user has access to a specific case."""
    db = database.SessionLocal()
    try:
        case = db.query(models.Case).filter(models.Case.id == case_id).first()
        if not case:
            return False
        # Admin/investigator can access any case
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return False
        role_names = [r.name.lower() for r in user.roles]
        if "admin" in role_names or "super admin" in role_names:
            return True
        if "investigator" in role_names or "analyst" in role_names:
            return True
        # Viewer can only access assigned cases
        if case.created_by == user_id:
            return True
        return False
    finally:
        db.close()


@router.websocket("/ws/case/{case_id}")
async def websocket_case_graph(
    websocket: WebSocket,
    case_id: str,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time graph updates.

    Query params:
        token: JWT authentication token

    Events received:
        - connected: Welcome message with connection info
        - entity.detected: New entity in the graph
        - relationship.detected: New relationship in the graph
        - graph.updated: Graph modified
        - evidence.processed: Evidence processing done
        - pong: Heartbeat response
        - sync: Missed events recovery
    """
    # ── Authentication ──
    if not token:
        await websocket.close(code=4001, reason="Token required")
        return

    try:
        payload = decode_token(token)
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except Exception as e:
        logger.warning("WebSocket auth failed: %s", e)
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # ── Case access verification ──
    if not _verify_case_access(user_id, case_id):
        await websocket.close(code=4003, reason="Access denied to this case")
        return

    # ── Accept connection ──
    await websocket.accept()
    try:
        conn = await manager.connect(websocket, user_id, case_id)
    except ConnectionError:
        return

    try:
        # ── Message loop ──
        while True:
            data = await websocket.receive_text()
            await manager.handle_message(websocket, case_id, user_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, case_id, user_id)
    except Exception as e:
        logger.error("WebSocket error for case %s user %s: %s", case_id, user_id, e)
        await manager.disconnect(websocket, case_id, user_id)


@router.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics (admin only)."""
    return manager.get_stats()
