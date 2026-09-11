"""
Realtime event relay for CrimeKit.

Bridges the domain-event bus (Redis pub/sub) to the authenticated,
case-scoped WebSocket connections managed by websocket_manager.

Without this relay, domain events are published to Redis but never
reached connected frontend clients — the WebSocket layer stayed silent
and the UI only updated via polling. This module subscribes to
``crimekit:events:case:*`` and forwards each event to
``manager.broadcast_to_case``.

The frontend's useGraphWebSocket hook reads ``event.type`` (not
``event_type``), so we map the field before broadcasting.
"""

import os
import re
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

# crimekit:events:case:{case_id}
_CHANNEL_RE = re.compile(r"^crimekit:events:case:(.+)$")
_TSK_CHANNEL_RE = re.compile(r"^crimekit:forensic:([^:]+):([^:]+)$")


async def run_event_relay():
    """Subscribe to domain-event channels and relay them to WebSocket clients."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        import redis.asyncio as aioredis
    except Exception as e:  # pragma: no cover
        logger.warning("Realtime relay: redis.asyncio unavailable (%s) — events will not be pushed", e)
        return

    pubsub = None
    try:
        client = aioredis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=None,     # never time out while waiting for events
            retry_on_timeout=True,
            health_check_interval=30,
        )
    except Exception as e:
        logger.warning("Realtime relay cannot connect to Redis (%s) — events will not be pushed", e)
        return

    from .websocket_manager import manager

    # Resilient loop: if the subscription dies (redis restart, network blip),
    # reconnect with backoff instead of terminating the relay permanently.
    backoff = 1
    while True:
        try:
            pubsub = client.pubsub()
            await pubsub.psubscribe("crimekit:events:case:*")
            await pubsub.psubscribe("crimekit:forensic:*:*")
            logger.info("Realtime relay subscribed to domain and TSK forensic channels")
            backoff = 1

            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message is None:
                    await asyncio.sleep(0.05)
                    continue
                if message.get("type") != "pmessage":
                    continue
                channel = message.get("channel", "")
                data = message.get("data")
                match = _CHANNEL_RE.match(channel)
                tsk_match = _TSK_CHANNEL_RE.match(channel)
                if not match and not tsk_match:
                    continue
                case_id = match.group(1) if match else tsk_match.group(1)
                try:
                    event = json.loads(data) if isinstance(data, str) else data
                    # Frontend hook expects `type`, not `event_type`.
                    if "type" not in event and "event_type" in event:
                        event["type"] = event["event_type"]
                    if tsk_match:
                        case_id = tsk_match.group(1)
                        event["type"] = event.get("event_type", event.get("type", "forensic.event"))
                        event["source"] = "tsk"
                    await manager.broadcast_to_case(case_id, event)
                except Exception as e:  # pragma: no cover
                    logger.warning("Realtime relay failed to broadcast event: %s", e)
        except asyncio.CancelledError:
            logger.info("Realtime relay cancelled")
            break
        except Exception as e:  # pragma: no cover
            logger.error("Realtime relay stopped: %s (reconnecting in %ss)", e, backoff)
            try:
                if pubsub:
                    await pubsub.aclose()
            except Exception:
                pass
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)
