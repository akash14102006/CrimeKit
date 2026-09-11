"""
Domain event system for CrimeKit.

Provides event publishing and Redis pub/sub for broadcasting
graph changes to connected WebSocket clients.

Event types:
- entity.detected: New entity extracted from evidence
- entity.resolved: Entity merged/resolved with another
- relationship.detected: New relationship extracted
- relationship.verified: Relationship confirmed by analyst
- graph.node.created: New node added to knowledge graph
- graph.edge.created: New edge added to knowledge graph
- graph.updated: Graph modified in any way
- evidence.processed: Evidence processing completed
- timeline.event.created: New timeline event added
"""

import os
import json
import time
import logging
import uuid
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ── Redis pub/sub lazy loading ──

_redis_client = None
_redis_available = None
_redis_last_attempt = 0.0
_REDIS_RETRY_INTERVAL = 5.0  # seconds between reconnection attempts


def _get_redis():
    """Lazy-load Redis client for pub/sub.

    Re-attempts connection on a cooldown instead of caching failure
    permanently. A transient Redis outage (or a startup race where the
    first publish happens before Redis is ready) must not disable the
    event bus forever — otherwise domain events never reach the relay /
    WebSocket subscribers.
    """
    global _redis_client, _redis_available, _redis_last_attempt
    if _redis_available is True:
        return _redis_client
    now = time.time()
    if _redis_available is False and (now - _redis_last_attempt) < _REDIS_RETRY_INTERVAL:
        return _redis_client
    _redis_last_attempt = now
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        client = redis.from_url(redis_url, socket_timeout=5, decode_responses=True)
        client.ping()
        _redis_client = client
        _redis_available = True
        logger.info("Redis pub/sub connected: %s", redis_url)
    except ImportError:
        _redis_available = False
        logger.info("redis package not installed — events will be in-memory only")
    except Exception as e:
        _redis_available = False
        _redis_client = None
        logger.warning("Redis connection failed: %s — events will be in-memory only", e)
    return _redis_client


# ── Event data model ──

@dataclass
class DomainEvent:
    """A domain event for the knowledge graph pipeline."""
    event_type: str
    case_id: str
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_name: Optional[str] = None
    source_entity_id: Optional[str] = None
    target_entity_id: Optional[str] = None
    relationship: Optional[str] = None
    evidence_id: Optional[str] = None
    artifact_id: Optional[str] = None
    confidence: Optional[float] = None
    processor: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Remove None values for cleaner JSON
        return {k: v for k, v in d.items() if v is not None}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data: str) -> "DomainEvent":
        d = json.loads(data)
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── In-memory event buffer (for when Redis is unavailable) ──

_in_memory_events: list = []
_in_memory_max_size = 1000


# ── Event publishing ──

def publish_event(event: DomainEvent) -> bool:
    """
    Publish a domain event to Redis pub/sub.

    Channel: crimekit:events:case:{case_id}
    Falls back to in-memory buffer if Redis is unavailable.

    Returns True if published successfully.
    """
    global _redis_available
    channel = f"crimekit:events:case:{event.case_id}"
    payload = event.to_json()
    logger.info("PUBLISH_EVENT enter type=%s redis_avail=%s", event.event_type, _redis_available)

    # Try Redis pub/sub
    redis_client = _get_redis()
    if redis_client:
        try:
            n = redis_client.publish(channel, payload)
            # Also store in a stream for missed-event recovery
            stream_key = f"crimekit:events:stream:{event.case_id}"
            redis_client.xadd(
                stream_key,
                {"event": payload},
                maxlen=1000,
                approximate=True,
            )
            logger.info("PUBLISHED %s -> %s (subscribers=%s)", event.event_type, channel, n)
            return True
        except Exception as e:
            _redis_available = False
            logger.warning("Redis publish failed: %s — falling back to in-memory", e)

    # Fallback: in-memory buffer
    logger.warning(
        "publish_event: redis client unavailable (available=%s) — buffering event %s in-memory only",
        _redis_available, event.event_type,
    )
    global _in_memory_events
    _in_memory_events.append({
        "channel": channel,
        "event": event.to_dict(),
        "timestamp": time.time(),
    })
    if len(_in_memory_events) > _in_memory_max_size:
        _in_memory_events = _in_memory_events[-_in_memory_max_size:]
    return False


def get_recent_events(case_id: str, since_timestamp: Optional[float] = None) -> list:
    """
    Get recent events for a case (for missed-event recovery).

    Tries Redis streams first, falls back to in-memory buffer.
    """
    # Try Redis streams
    redis_client = _get_redis()
    if redis_client:
        try:
            stream_key = f"crimekit:events:stream:{case_id}"
            start_id = "0"
            if since_timestamp:
                # Convert timestamp to Redis stream ID (approximate)
                start_id = f"{int(since_timestamp * 1000)}-0"
            entries = redis_client.xrange(stream_key, min=start_id, count=100)
            events = []
            for entry_id, fields in entries:
                event_data = json.loads(fields.get("event", "{}"))
                events.append(event_data)
            return events
        except Exception as e:
            logger.warning("Redis stream read failed: %s", e)

    # Fallback: in-memory buffer
    if since_timestamp:
        return [
            e["event"]
            for e in _in_memory_events
            if e["channel"].endswith(case_id) and e["timestamp"] >= since_timestamp
        ]
    return [
        e["event"]
        for e in _in_memory_events
        if e["channel"].endswith(case_id)
    ]


# ── Convenience event publishers ──

def publish_entity_detected(
    case_id: str,
    entity_name: str,
    entity_type: str,
    evidence_id: Optional[str] = None,
    confidence: Optional[float] = None,
    processor: Optional[str] = None,
):
    """Publish an entity.detected event."""
    event = DomainEvent(
        event_type="entity.detected",
        case_id=case_id,
        entity_name=entity_name,
        entity_type=entity_type,
        evidence_id=evidence_id,
        confidence=confidence,
        processor=processor,
    )
    return publish_event(event)


def publish_relationship_detected(
    case_id: str,
    source_entity: str,
    target_entity: str,
    relationship: str,
    evidence_id: Optional[str] = None,
    confidence: Optional[float] = None,
    processor: Optional[str] = None,
):
    """Publish a relationship.detected event."""
    event = DomainEvent(
        event_type="relationship.detected",
        case_id=case_id,
        source_entity_id=source_entity,
        target_entity_id=target_entity,
        relationship=relationship,
        evidence_id=evidence_id,
        confidence=confidence,
        processor=processor,
    )
    return publish_event(event)


def publish_graph_updated(case_id: str, metadata: Optional[Dict[str, Any]] = None):
    """Publish a graph.updated event."""
    event = DomainEvent(
        event_type="graph.updated",
        case_id=case_id,
        metadata=metadata or {},
    )
    return publish_event(event)


def publish_evidence_processed(
    case_id: str,
    evidence_id: str,
    entity_count: int = 0,
    relationship_count: int = 0,
):
    """Publish an evidence.processed event."""
    event = DomainEvent(
        event_type="evidence.processed",
        case_id=case_id,
        evidence_id=evidence_id,
        metadata={
            "entity_count": entity_count,
            "relationship_count": relationship_count,
        },
    )
    return publish_event(event)
