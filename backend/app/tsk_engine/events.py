"""Real-time forensic event streaming — Redis pub/sub events from TSK worker."""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ForensicEventType(str, Enum):
    STAGE_STARTED = "forensic.stage.started"
    STAGE_PROGRESS = "forensic.stage.progress"
    STAGE_COMPLETED = "forensic.stage.completed"
    STAGE_FAILED = "forensic.stage.failed"
    ARTIFACT_DISCOVERED = "forensic.artifact.discovered"
    FILE_DISCOVERED = "forensic.file.discovered"
    TIMELINE_CREATED = "forensic.timeline.created"
    ENTITY_DETECTED = "forensic.entity.detected"
    ENTITY_RESOLVED = "forensic.entity.resolved"
    RELATIONSHIP_DETECTED = "forensic.relationship.detected"
    PROCESSING_COMPLETED = "forensic.processing.completed"
    PROCESSING_FAILED = "forensic.processing.failed"
    PROCESSING_CANCELLED = "forensic.processing.cancelled"
    CHECKPOINT_SAVED = "forensic.checkpoint.saved"
    PARTITION_DISCOVERED = "forensic.partition.discovered"
    FILESYSTEM_DETECTED = "forensic.filesystem.detected"


@dataclass
class ForensicEvent:
    event_id: str
    event_type: ForensicEventType
    case_id: str
    evidence_id: str
    processor: str
    stage: str
    timestamp: str
    correlation_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    worker_id: Optional[str] = None


class ForensicEventEmitter:
    """Emits structured forensic events via Redis pub/sub and in-process callbacks.

    Events are published to Redis channels for real-time WebSocket relay
    and also stored in an in-memory buffer for immediate consumption.
    """

    def __init__(
        self,
        case_id: str,
        evidence_id: str,
        worker_id: Optional[str] = None,
        redis_client: Optional[Any] = None,
    ) -> None:
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.worker_id = worker_id
        self._redis = redis_client
        self._events: List[ForensicEvent] = []
        self._callbacks: List[Callable[[ForensicEvent], None]] = []
        self._correlation_id = str(uuid.uuid4())
        self._start_time = time.monotonic()

    def add_callback(self, cb: Callable[[ForensicEvent], None]) -> None:
        self._callbacks.append(cb)

    def _elapsed_ms(self) -> float:
        return (time.monotonic() - self._start_time) * 1000

    def emit(
        self,
        event_type: ForensicEventType,
        stage: str,
        data: Optional[Dict[str, Any]] = None,
        processor: str = "tsk",
    ) -> ForensicEvent:
        event = ForensicEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            case_id=self.case_id,
            evidence_id=self.evidence_id,
            processor=processor,
            stage=stage,
            timestamp=datetime.now(timezone.utc).isoformat(),
            correlation_id=self._correlation_id,
            data=data or {},
            worker_id=self.worker_id,
        )
        event.data["elapsed_ms"] = round(self._elapsed_ms(), 2)
        self._events.append(event)

        for cb in self._callbacks:
            try:
                cb(event)
            except Exception as exc:
                logger.warning("Event callback error: %s", exc)

        if self._redis:
            try:
                channel = f"crimekit:forensic:{self.case_id}:{self.evidence_id}"
                self._redis.publish(channel, json.dumps({
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "case_id": event.case_id,
                    "evidence_id": event.evidence_id,
                    "processor": event.processor,
                    "stage": event.stage,
                    "timestamp": event.timestamp,
                    "correlation_id": event.correlation_id,
                    "data": event.data,
                    "worker_id": event.worker_id,
                }))
            except Exception as exc:
                logger.debug("Redis publish failed: %s", exc)

        return event

    def stage_started(self, stage: str, **data: Any) -> ForensicEvent:
        return self.emit(ForensicEventType.STAGE_STARTED, stage, data)

    def stage_progress(self, stage: str, **data: Any) -> ForensicEvent:
        return self.emit(ForensicEventType.STAGE_PROGRESS, stage, data)

    def stage_completed(self, stage: str, **data: Any) -> ForensicEvent:
        return self.emit(ForensicEventType.STAGE_COMPLETED, stage, data)

    def stage_failed(self, stage: str, error: str, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["error"] = error
        return self.emit(ForensicEventType.STAGE_FAILED, stage, d)

    def artifact_discovered(self, artifact_id: str, file_path: str, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["artifact_id"] = artifact_id
        d["file_path"] = file_path
        return self.emit(ForensicEventType.ARTIFACT_DISCOVERED, "artifact_extraction", d)

    def file_discovered(self, file_path: str, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["file_path"] = file_path
        return self.emit(ForensicEventType.FILE_DISCOVERED, "file_enumeration", d)

    def timeline_created(self, event_count: int, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["event_count"] = event_count
        return self.emit(ForensicEventType.TIMELINE_CREATED, "timeline_generation", d)

    def entity_detected(self, entity_name: str, entity_type: str, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["entity_name"] = entity_name
        d["entity_type"] = entity_type
        return self.emit(ForensicEventType.ENTITY_DETECTED, "entity_extraction", d)

    def relationship_detected(self, source: str, target: str, rel_type: str, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["source"] = source
        d["target"] = target
        d["relationship_type"] = rel_type
        return self.emit(ForensicEventType.RELATIONSHIP_DETECTED, "relationship_discovery", d)

    def partition_discovered(self, index: int, description: str, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["partition_index"] = index
        d["description"] = description
        return self.emit(ForensicEventType.PARTITION_DISCOVERED, "partition_discovery", d)

    def filesystem_detected(self, fs_type: str, offset: int, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["filesystem_type"] = fs_type
        d["offset"] = offset
        return self.emit(ForensicEventType.FILESYSTEM_DETECTED, "filesystem_detection", d)

    def processing_completed(self, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["total_events"] = len(self._events)
        d["total_duration_ms"] = round(self._elapsed_ms(), 2)
        return self.emit(ForensicEventType.PROCESSING_COMPLETED, "processing_complete", d)

    def processing_failed(self, error: str, **data: Any) -> ForensicEvent:
        d = dict(data)
        d["error"] = error
        return self.emit(ForensicEventType.PROCESSING_FAILED, "processing_failed", d)

    def get_events(self) -> List[ForensicEvent]:
        return list(self._events)

    def get_event_log(self) -> List[str]:
        logs = []
        for ev in self._events:
            elapsed = ev.data.get("elapsed_ms", 0)
            status = "OK" if ev.event_type != ForensicEventType.STAGE_FAILED else "FAIL"
            stage_display = ev.stage.replace("_", " ").upper()
            logs.append(f"[{elapsed:8.3f}] {stage_display:<40s} {status}")
        return logs
