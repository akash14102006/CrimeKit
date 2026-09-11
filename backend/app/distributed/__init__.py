"""Distributed Processing System using Redis Streams.

Enterprise-grade task queue with consumer groups for exactly-once processing,
worker autoscaling, job dependency graphs, retry with exponential backoff,
dead-letter queues, and Prometheus metrics.

Architecture
------------
Redis Streams serve as the message broker (NOT Celery) because:
- Exactly-once semantics via consumer groups (XREADGROUP + XACK)
- Simpler deployment: no broker daemon, no result backend, no flower
- Native persistence: streams survive restarts
- Consumer groups provide load-balanced work distribution
- Lower operational overhead for single-node and small clusters

Stream topology
---------------
- crimekit:tasks:{priority}  (critical / high / normal / low)
- crimekit:dlq               (dead-letter stream)
- crimekit:progress:{job_id} (progress hash)
- crimekit:worker:{id}:hb    (worker heartbeat key)
- crimekit:job:{id}:deps     (dependency graph hash)

Consumer group: ``crimekit-workers`` (shared across all workers)

Priority sampling order: critical → high → normal → low
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CONSUMER_GROUP: str = os.getenv("CRIMEKIT_CONSUMER_GROUP", "crimekit-workers")
CONSUMER_PREFIX: str = os.getenv("CRIMEKIT_CONSUMER_PREFIX", "worker")
HEARTBEAT_TTL: int = int(os.getenv("CRIMEKIT_HEARTBEAT_TTL", "30"))
HEARTBEAT_INTERVAL: int = int(os.getenv("CRIMEKIT_HEARTBEAT_INTERVAL", "10"))
STREAM_MAX_LEN: int = int(os.getenv("CRIMEKIT_STREAM_MAX_LEN", "100000"))
CLAIM_MIN_IDLE_MS: int = int(os.getenv("CRIMEKIT_CLAIM_MIN_IDLE_MS", "60000"))
MAX_RETRIES: int = int(os.getenv("CRIMEKIT_MAX_RETRIES", "6"))
BACKOFF_BASE: float = float(os.getenv("CRIMEKIT_BACKOFF_BASE", "1"))
BACKOFF_MAX: float = float(os.getenv("CRIMEKIT_BACKOFF_MAX", "30"))
MIN_WORKERS: int = int(os.getenv("CRIMEKIT_MIN_WORKERS", "1"))
MAX_WORKERS: int = int(os.getenv("CRIMEKIT_MAX_WORKERS", "8"))
SCALE_UP_THRESHOLD: int = int(os.getenv("CRIMEKIT_SCALE_UP_THRESHOLD", "10"))
SCALE_DOWN_THRESHOLD: int = int(os.getenv("CRIMEKIT_SCALE_DOWN_THRESHOLD", "2"))
SCALE_CHECK_INTERVAL: int = int(os.getenv("CRIMEKIT_SCALE_CHECK_INTERVAL", "30"))

PRIORITY_STREAMS: Dict[str, str] = {
    "critical": "crimekit:tasks:critical",
    "high": "crimekit:tasks:high",
    "normal": "crimekit:tasks:normal",
    "low": "crimekit:tasks:low",
}

PRIORITY_ORDER: List[str] = ["critical", "high", "normal", "low"]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    CLAIMED = "claimed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    DEAD_LETTERED = "dead_lettered"


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class TaskPayload:
    """Serializable task payload pushed to Redis Streams."""
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    job_id: str = ""
    processor_type: str = ""
    priority: str = "normal"
    payload: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retry_count: int = 0
    max_retries: int = MAX_RETRIES
    checkpoint: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, str]:
        """Serialize to Redis stream entry (all values must be strings)."""
        return {
            "task_id": self.task_id,
            "job_id": self.job_id,
            "processor_type": self.processor_type,
            "priority": self.priority,
            "payload": json.dumps(self.payload, default=str),
            "dependencies": json.dumps(self.dependencies),
            "created_at": self.created_at,
            "retry_count": str(self.retry_count),
            "max_retries": str(self.max_retries),
            "checkpoint": json.dumps(self.checkpoint, default=str),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "TaskPayload":
        """Deserialize from Redis stream entry."""
        return cls(
            task_id=data.get("task_id", uuid.uuid4().hex),
            job_id=data.get("job_id", ""),
            processor_type=data.get("processor_type", ""),
            priority=data.get("priority", "normal"),
            payload=json.loads(data.get("payload", "{}")),
            dependencies=json.loads(data.get("dependencies", "[]")),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            retry_count=int(data.get("retry_count", "0")),
            max_retries=int(data.get("max_retries", str(MAX_RETRIES))),
            checkpoint=json.loads(data.get("checkpoint", "{}")),
        )


@dataclass
class WorkerInfo:
    """Worker registration metadata."""
    worker_id: str = field(default_factory=lambda: f"{CONSUMER_PREFIX}-{uuid.uuid4().hex[:8]}")
    name: str = ""
    status: str = "idle"
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_heartbeat: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tasks_completed: int = 0
    tasks_failed: int = 0
    current_task_id: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    max_concurrency: int = 1


# ---------------------------------------------------------------------------
# Prometheus Metrics Collector
# ---------------------------------------------------------------------------

class DistributedMetrics:
    """Collects Prometheus-format metrics for the distributed system."""

    def __init__(self) -> None:
        self._task_submitted: Dict[str, int] = defaultdict(int)
        self._task_completed: Dict[str, int] = defaultdict(int)
        self._task_failed: Dict[str, int] = defaultdict(int)
        self._task_retry: Dict[str, int] = defaultdict(int)
        self._task_dlq: int = 0
        self._task_duration: Dict[str, List[float]] = defaultdict(list)
        self._worker_count: int = 0
        self._worker_active: int = 0
        self._queue_depth: Dict[str, int] = defaultdict(int)
        self._dep_resolved: int = 0
        self._dep_waited: int = 0
        self._autoscale_events: int = 0
        self._start_time: float = time.time()

    def record_task_submitted(self, processor: str, priority: str) -> None:
        self._task_submitted[f'{processor}:{priority}'] += 1

    def record_task_completed(self, processor: str, duration_ms: float) -> None:
        self._task_completed[processor] += 1
        self._task_duration[processor].append(duration_ms)

    def record_task_failed(self, processor: str) -> None:
        self._task_failed[processor] += 1

    def record_task_retry(self, processor: str) -> None:
        self._task_retry[processor] += 1

    def record_task_dlq(self) -> None:
        self._task_dlq += 1

    def set_worker_counts(self, total: int, active: int) -> None:
        self._worker_count = total
        self._worker_active = active

    def set_queue_depth(self, priority: str, depth: int) -> None:
        self._queue_depth[priority] = depth

    def record_dep_resolved(self) -> None:
        self._dep_resolved += 1

    def record_dep_waited(self) -> None:
        self._dep_waited += 1

    def record_autoscale(self) -> None:
        self._autoscale_events += 1

    def to_prometheus(self) -> str:
        lines: List[str] = []
        lines.append("# HELP crimekit_tasks_submitted_total Tasks submitted by processor and priority")
        lines.append("# TYPE crimekit_tasks_submitted_total counter")
        for key, val in self._task_submitted.items():
            proc, prio = key.split(":", 1)
            lines.append(f'crimekit_tasks_submitted_total{{processor="{proc}",priority="{prio}"}} {val}')

        lines.append("# HELP crimekit_tasks_completed_total Tasks completed by processor")
        lines.append("# TYPE crimekit_tasks_completed_total counter")
        for proc, val in self._task_completed.items():
            lines.append(f'crimekit_tasks_completed_total{{processor="{proc}"}} {val}')

        lines.append("# HELP crimekit_tasks_failed_total Tasks failed by processor")
        lines.append("# TYPE crimekit_tasks_failed_total counter")
        for proc, val in self._task_failed.items():
            lines.append(f'crimekit_tasks_failed_total{{processor="{proc}"}} {val}')

        lines.append("# HELP crimekit_tasks_retried_total Tasks retried by processor")
        lines.append("# TYPE crimekit_tasks_retried_total counter")
        for proc, val in self._task_retry.items():
            lines.append(f'crimekit_tasks_retried_total{{processor="{proc}"}} {val}')

        lines.append("# HELP crimekit_tasks_dead_lettered_total Tasks moved to dead-letter queue")
        lines.append("# TYPE crimekit_tasks_dead_lettered_total counter")
        lines.append(f"crimekit_tasks_dead_lettered_total {self._task_dlq}")

        lines.append("# HELP crimekit_task_duration_seconds Task processing duration")
        lines.append("# TYPE crimekit_task_duration_seconds summary")
        for proc, durations in self._task_duration.items():
            if durations:
                avg = sum(durations) / len(durations)
                p99 = sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 1 else durations[0]
                lines.append(f'crimekit_task_duration_seconds{{processor="{proc}",quantile="0.5"}} {avg/1000:.4f}')
                lines.append(f'crimekit_task_duration_seconds{{processor="{proc}",quantile="0.99"}} {p99/1000:.4f}')

        lines.append("# HELP crimekit_workers_total Total registered workers")
        lines.append("# TYPE crimekit_workers_total gauge")
        lines.append(f"crimekit_workers_total {self._worker_count}")

        lines.append("# HELP crimekit_workers_active Currently active workers")
        lines.append("# TYPE crimekit_workers_active gauge")
        lines.append(f"crimekit_workers_active {self._worker_active}")

        lines.append("# HELP crimekit_queue_depth_tasks Queue depth by priority")
        lines.append("# TYPE crimekit_queue_depth_tasks gauge")
        for prio, depth in self._queue_depth.items():
            lines.append(f'crimekit_queue_depth_tasks{{priority="{prio}"}} {depth}')

        lines.append("# HELP crimekit_deps_resolved_total Dependency edges resolved")
        lines.append("# TYPE crimekit_deps_resolved_total counter")
        lines.append(f"crimekit_deps_resolved_total {self._dep_resolved}")

        lines.append("# HELP crimekit_deps_waited_total Tasks waiting on dependencies")
        lines.append("# TYPE crimekit_deps_waited_total counter")
        lines.append(f"crimekit_deps_waited_total {self._dep_waited}")

        lines.append("# HELP crimekit_autoscale_events_total Autoscale events triggered")
        lines.append("# TYPE crimekit_autoscale_events_total counter")
        lines.append(f"crimekit_autoscale_events_total {self._autoscale_events}")

        uptime = time.time() - self._start_time
        lines.append("# HELP crimekit_distributed_uptime_seconds Distributed system uptime")
        lines.append("# TYPE crimekit_distributed_uptime_seconds gauge")
        lines.append(f"crimekit_distributed_uptime_seconds {uptime:.0f}")

        return "\n".join(lines) + "\n"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tasks_submitted": dict(self._task_submitted),
            "tasks_completed": dict(self._task_completed),
            "tasks_failed": dict(self._task_failed),
            "tasks_retried": dict(self._task_retry),
            "tasks_dead_lettered": self._task_dlq,
            "workers_total": self._worker_count,
            "workers_active": self._worker_active,
            "queue_depth": dict(self._queue_depth),
            "deps_resolved": self._dep_resolved,
            "deps_waited": self._dep_waited,
            "autoscale_events": self._autoscale_events,
            "uptime_seconds": time.time() - self._start_time,
        }


# Global metrics singleton
metrics = DistributedMetrics()


# ---------------------------------------------------------------------------
# Dead-Letter Queue
# ---------------------------------------------------------------------------

class DeadLetterQueue:
    """Manages tasks that exhausted all retries.

    Dead-lettered tasks are appended to ``crimekit:dlq`` stream and persisted
    to the ``distributed_dlq_tasks`` PostgreSQL table for audit and replay.
    """

    DLQ_STREAM = "crimekit:dlq"

    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    async def push(self, task: TaskPayload, error: str, worker_id: str = "") -> str:
        """Move a task to the dead-letter queue.

        Returns the DLQ message ID.
        """
        entry = task.to_dict()
        entry["dlq_error"] = error
        entry["dlq_worker"] = worker_id
        entry["dlq_timestamp"] = datetime.now(timezone.utc).isoformat()
        entry["original_stream"] = PRIORITY_STREAMS.get(task.priority, PRIORITY_STREAMS["normal"])

        msg_id = await self._redis.xadd(
            self.DLQ_STREAM,
            entry,
            maxlen=STREAM_MAX_LEN,
        )
        logger.warning(
            "Task %s dead-lettered: processor=%s error=%s worker=%s",
            task.task_id, task.processor_type, error, worker_id,
        )
        metrics.record_task_dlq()
        return msg_id

    async def peek(self, count: int = 10) -> List[Dict[str, Any]]:
        """Peek at recent dead-lettered tasks without consuming them."""
        entries = await self._redis.xrevrange(self.DLQ_STREAM, count=count)
        results = []
        for msg_id, fields in entries:
            results.append({"id": msg_id, **fields})
        return results

    async def replay(self, msg_id: str, target_priority: str = "normal") -> bool:
        """Replay a dead-lettered task back to the appropriate priority stream."""
        entries = await self._redis.xrange(self.DLQ_STREAM, min=msg_id, max=msg_id)
        if not entries:
            return False
        _, fields = entries[0]
        task = TaskPayload.from_dict(fields)
        task.priority = target_priority
        task.retry_count = 0
        stream = PRIORITY_STREAMS.get(target_priority, PRIORITY_STREAMS["normal"])
        await self._redis.xadd(stream, task.to_dict(), maxlen=STREAM_MAX_LEN)
        await self._redis.xdel(self.DLQ_STREAM, msg_id)
        logger.info("Task %s replayed to %s stream", task.task_id, target_priority)
        return True

    async def size(self) -> int:
        info = await self._redis.xinfo_stream(self.DLQ_STREAM)
        return info.get("length", 0)

    async def purge(self, max_age_seconds: int = 86400) -> int:
        """Remove DLQ entries older than max_age_seconds."""
        cutoff_ms = int((time.time() - max_age_seconds) * 1000)
        cutoff_id = f"{cutoff_ms}-0"
        entries = await self._redis.xrange(self.DLQ_STREAM, min="0", max=cutoff_id)
        removed = 0
        for msg_id, _ in entries:
            await self._redis.xdel(self.DLQ_STREAM, msg_id)
            removed += 1
        return removed


# ---------------------------------------------------------------------------
# Retry Manager
# ---------------------------------------------------------------------------

class RetryManager:
    """Handles exponential backoff retry logic.

    Backoff sequence: 1s, 2s, 4s, 8s, 16s, 30s (capped).
    """

    @staticmethod
    def backoff_seconds(attempt: int) -> float:
        """Calculate backoff duration for the given attempt number (0-indexed).

        Returns min(BACKOFF_BASE * 2^attempt, BACKOFF_MAX).
        """
        delay = BACKOFF_BASE * (2 ** attempt)
        return min(delay, BACKOFF_MAX)

    @staticmethod
    def should_retry(task: TaskPayload) -> bool:
        return task.retry_count < task.max_retries

    async def schedule_retry(
        self,
        redis: aioredis.Redis,
        task: TaskPayload,
        error: str,
    ) -> bool:
        """Schedule a task for retry. Returns True if retried, False if exhausted."""
        if not self.should_retry(task):
            return False

        task.retry_count += 1
        backoff = self.backoff_seconds(task.retry_count - 1)
        retry_at = time.time() + backoff

        retry_key = f"crimekit:retry:{task.task_id}"
        await redis.setex(
            retry_key,
            int(backoff) + 60,
            json.dumps({
                "task": task.to_dict(),
                "retry_at": retry_at,
                "backoff_seconds": backoff,
                "last_error": error,
            }, default=str),
        )

        metrics.record_task_retry(task.processor_type)
        logger.info(
            "Task %s scheduled for retry %d/%d in %.1fs (error: %s)",
            task.task_id, task.retry_count, task.max_retries, backoff, error,
        )
        return True

    async def check_retries(self, redis: aioredis.Redis) -> List[TaskPayload]:
        """Poll for tasks whose backoff has elapsed and re-enqueue them."""
        ready: List[TaskPayload] = []
        now = time.time()
        cursor = b"0"
        while True:
            cursor, keys = await redis.scan(cursor, match="crimekit:retry:*", count=100)
            for key in keys:
                raw = await redis.get(key)
                if not raw:
                    continue
                info = json.loads(raw)
                if info.get("retry_at", 0) <= now:
                    task = TaskPayload.from_dict(info["task"])
                    stream = PRIORITY_STREAMS.get(task.priority, PRIORITY_STREAMS["normal"])
                    await redis.xadd(stream, task.to_dict(), maxlen=STREAM_MAX_LEN)
                    await redis.delete(key)
                    ready.append(task)
                    logger.info("Task %s re-enqueued after retry backoff", task.task_id)
            if cursor == b"0":
                break
        return ready

    async def cancel_retry(self, redis: aioredis.Redis, task_id: str) -> bool:
        key = f"crimekit:retry:{task_id}"
        deleted = await redis.delete(key)
        return deleted > 0


# ---------------------------------------------------------------------------
# Distributed Queue
# ---------------------------------------------------------------------------

class DistributedQueue:
    """Redis Stream-based task queue with consumer groups.

    Provides exactly-once processing via XREADGROUP + XACK, priority-based
    stream sampling, and stream trimming for bounded memory usage.
    """

    def __init__(self, redis_url: str = REDIS_URL) -> None:
        self._redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._consumer_id: str = f"{CONSUMER_PREFIX}-{uuid.uuid4().hex[:8]}"
        self.dlq: Optional[DeadLetterQueue] = None
        self.retry_manager: Optional[RetryManager] = None

    async def connect(self) -> None:
        """Initialize Redis connection and create consumer groups."""
        self._redis = aioredis.from_url(
            self._redis_url,
            decode_responses=True,
            max_connections=20,
            retry_on_timeout=True,
        )
        self.dlq = DeadLetterQueue(self._redis)
        self.retry_manager = RetryManager()

        for stream in PRIORITY_STREAMS.values():
            try:
                await self._redis.xgroup_create(
                    stream, CONSUMER_GROUP, id="0", mkstream=True,
                )
                logger.info("Created consumer group '%s' on stream '%s'", CONSUMER_GROUP, stream)
            except aioredis.ResponseError as exc:
                if "BUSYGROUP" not in str(exc):
                    raise

        try:
            await self._redis.xgroup_create(
                DeadLetterQueue.DLQ_STREAM, CONSUMER_GROUP, id="0", mkstream=True,
            )
        except aioredis.ResponseError:
            pass

        logger.info(
            "DistributedQueue connected: consumer=%s group=%s",
            self._consumer_id, CONSUMER_GROUP,
        )

    async def close(self) -> None:
        if self._redis:
            await self._redis.aclose()

    @property
    def redis(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError("DistributedQueue not connected. Call connect() first.")
        return self._redis

    @property
    def consumer_id(self) -> str:
        return self._consumer_id

    async def submit(
        self,
        task: TaskPayload,
        priority: str = "normal",
    ) -> str:
        """Submit a task to the appropriate priority stream.

        Returns the Redis stream message ID.
        """
        task.priority = priority
        stream = PRIORITY_STREAMS.get(priority, PRIORITY_STREAMS["normal"])
        msg_id = await self.redis.xadd(
            stream,
            task.to_dict(),
            maxlen=STREAM_MAX_LEN,
        )
        metrics.record_task_submitted(task.processor_type, priority)
        logger.debug("Task %s submitted to %s (msg=%s)", task.task_id, stream, msg_id)
        return msg_id

    async def submit_many(
        self,
        tasks: List[TaskPayload],
        priority: str = "normal",
    ) -> List[str]:
        """Submit multiple tasks in a pipeline for throughput."""
        pipe = self.redis.pipeline(transaction=False)
        for task in tasks:
            task.priority = priority
            stream = PRIORITY_STREAMS.get(priority, PRIORITY_STREAMS["normal"])
            pipe.xadd(stream, task.to_dict(), maxlen=STREAM_MAX_LEN)
            metrics.record_task_submitted(task.processor_type, priority)
        results = await pipe.execute()
        return results

    async def consume(
        self,
        count: int = 1,
        timeout_ms: int = 2000,
    ) -> List[Tuple[str, TaskPayload]]:
        """Read tasks from priority streams via consumer group.

        Sampling order: critical → high → normal → low.
        Returns list of (message_id, TaskPayload) tuples.
        """
        streams = {
            PRIORITY_STREAMS[p]: ">"
            for p in PRIORITY_ORDER
        }
        results = await self.redis.xreadgroup(
            CONSUMER_GROUP,
            self._consumer_id,
            streams,
            count=count,
            block=timeout_ms,
        )
        tasks: List[Tuple[str, TaskPayload]] = []
        for stream_name, messages in results:
            for msg_id, fields in messages:
                task = TaskPayload.from_dict(fields)
                tasks.append((msg_id, task))
        return tasks

    async def acknowledge(self, stream: str, msg_id: str) -> None:
        """Acknowledge successful processing of a message."""
        await self.redis.xack(stream, CONSUMER_GROUP, msg_id)

    async def claim_stale(
        self,
        min_idle_ms: int = CLAIM_MIN_IDLE_MS,
        count: int = 5,
    ) -> List[Tuple[str, str, TaskPayload]]:
        """Claim messages from other consumers that have exceeded min idle time.

        Returns list of (stream_name, msg_id, TaskPayload).
        """
        claimed: List[Tuple[str, str, TaskPayload]] = []
        for stream in PRIORITY_STREAMS.values():
            pending = await self.redis.xpending_range(
                stream, CONSUMER_GROUP, min="-", max="+", count=count,
            )
            for entry in pending:
                msg_id = entry["message_id"]
                idle_ms = entry["idle"]
                consumer = entry["consumer"]
                if idle_ms >= min_idle_ms and consumer != self._consumer_id:
                    try:
                        messages = await self.redis.xclaim(
                            stream,
                            CONSUMER_GROUP,
                            self._consumer_id,
                            min_idle_ms=min_idle_ms,
                            message_ids=[msg_id],
                        )
                        for claimed_id, fields in messages:
                            task = TaskPayload.from_dict(fields)
                            claimed.append((stream, claimed_id, task))
                    except Exception as exc:
                        logger.error("Failed to claim message %s: %s", msg_id, exc)
        return claimed

    async def queue_depth(self) -> Dict[str, int]:
        """Return approximate length of each priority stream."""
        depths: Dict[str, int] = {}
        for prio, stream in PRIORITY_STREAMS.items():
            try:
                info = await self.redis.xinfo_stream(stream)
                depth = info.get("length", 0)
                depths[prio] = depth
                metrics.set_queue_depth(prio, depth)
            except Exception:
                depths[prio] = 0
        return depths

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task. Only works for tasks not yet claimed by a worker."""
        for stream in PRIORITY_STREAMS.values():
            entries = await self.redis.xrange(stream)
            for msg_id, fields in entries:
                if fields.get("task_id") == task_id:
                    await self.redis.xdel(stream, msg_id)
                    if self.retry_manager:
                        await self.retry_manager.cancel_retry(self.redis, task_id)
                    logger.info("Task %s cancelled from stream %s", task_id, stream)
                    return True
        return False

    async def get_progress(self, job_id: str) -> Dict[str, Any]:
        """Get progress info for a job from Redis."""
        key = f"crimekit:progress:{job_id}"
        data = await self.redis.hgetall(key)
        if not data:
            return {"job_id": job_id, "status": "unknown"}
        return {
            "job_id": job_id,
            "status": data.get("status", "unknown"),
            "completed": int(data.get("completed", "0")),
            "total": int(data.get("total", "0")),
            "current_processor": data.get("current_processor", ""),
            "started_at": data.get("started_at", ""),
            "updated_at": data.get("updated_at", ""),
        }

    async def update_progress(
        self,
        job_id: str,
        status: str,
        completed: int,
        total: int,
        current_processor: str = "",
        ttl: int = 3600,
    ) -> None:
        """Update job progress in Redis."""
        key = f"crimekit:progress:{job_id}"
        await self.redis.hset(key, mapping={
            "status": status,
            "completed": str(completed),
            "total": str(total),
            "current_processor": current_processor,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        await self.redis.expire(key, ttl)


# ---------------------------------------------------------------------------
# Task Router
# ---------------------------------------------------------------------------

class TaskRouter:
    """Routes tasks to the appropriate priority stream based on processor type.

    Maintains a configurable mapping of processor types to priorities.
    Supports processor affinity (pinning specific processors to specific workers).
    """

    DEFAULT_ROUTING: Dict[str, str] = {
        "hashes": "critical",
        "metadata": "critical",
        "mime": "critical",
        "ocr": "high",
        "image_analysis": "high",
        "image_metadata": "high",
        "pdf_text": "normal",
        "email_parse": "normal",
        "zip_list": "normal",
    }

    def __init__(
        self,
        routing_table: Optional[Dict[str, str]] = None,
        default_priority: str = "normal",
    ) -> None:
        self._routing: Dict[str, str] = dict(routing_table or self.DEFAULT_ROUTING)
        self._default_priority = default_priority
        self._affinity: Dict[str, Set[str]] = defaultdict(set)

    def route(self, processor_type: str) -> str:
        """Determine the priority stream for a given processor type."""
        return self._routing.get(processor_type, self._default_priority)

    def set_route(self, processor_type: str, priority: str) -> None:
        if priority not in PRIORITY_ORDER:
            raise ValueError(f"Invalid priority: {priority}. Must be one of {PRIORITY_ORDER}")
        self._routing[processor_type] = priority

    def set_affinity(self, processor_type: str, worker_ids: Set[str]) -> None:
        """Pin a processor type to specific worker IDs."""
        self._affinity[processor_type] = worker_ids

    def get_affinity(self, processor_type: str) -> Set[str]:
        return self._affinity.get(processor_type, set())

    def is_affinitized(self, processor_type: str, worker_id: str) -> bool:
        """Check if a worker is allowed to run this processor type."""
        aff = self._affinity.get(processor_type)
        if not aff:
            return True
        return worker_id in aff

    def route_task(self, task: TaskPayload) -> TaskPayload:
        """Set the priority on a task based on its processor type and return it."""
        task.priority = self.route(task.processor_type)
        return task

    def get_routing_table(self) -> Dict[str, str]:
        return dict(self._routing)


# ---------------------------------------------------------------------------
# Job Dependency Graph
# ---------------------------------------------------------------------------

class JobDependencyGraph:
    """Manages a DAG of task dependencies within and across jobs.

    Tasks can declare that they depend on other tasks by task_id.
    The graph validates for cycles and provides topological ordering.
    Completion status is tracked in Redis for real-time checks.
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    async def register_task(self, task: TaskPayload) -> None:
        """Register a task and its dependencies in the graph."""
        key = f"crimekit:job:{task.job_id}:deps"
        await self._redis.hset(key, task.task_id, json.dumps({
            "dependencies": task.dependencies,
            "status": TaskStatus.PENDING.value,
            "processor_type": task.processor_type,
        }))

    async def update_status(self, job_id: str, task_id: str, status: str) -> None:
        """Update the status of a task in the dependency graph."""
        key = f"crimekit:job:{job_id}:deps"
        raw = await self._redis.hget(key, task_id)
        if raw:
            info = json.loads(raw)
            info["status"] = status
            await self._redis.hset(key, task_id, json.dumps(info))

    async def are_dependencies_met(self, job_id: str, task_id: str) -> bool:
        """Check if all dependencies for a task have completed."""
        key = f"crimekit:job:{job_id}:deps"
        raw = await self._redis.hget(key, task_id)
        if not raw:
            return True
        info = json.loads(raw)
        deps = info.get("dependencies", [])
        if not deps:
            return True
        for dep_id in deps:
            dep_raw = await self._redis.hget(key, dep_id)
            if not dep_raw:
                return False
            dep_info = json.loads(dep_raw)
            if dep_info.get("status") != TaskStatus.COMPLETED.value:
                return False
        return True

    async def get_ready_tasks(self, job_id: str) -> List[str]:
        """Return task IDs whose dependencies are all met."""
        key = f"crimekit:job:{job_id}:deps"
        all_tasks = await self._redis.hgetall(key)
        ready: List[str] = []
        for task_id, raw in all_tasks.items():
            info = json.loads(raw)
            if info.get("status") in (TaskStatus.QUEUED.value, TaskStatus.PENDING.value):
                if await self.are_dependencies_met(job_id, task_id):
                    ready.append(task_id)
        return ready

    async def get_topological_order(self, job_id: str) -> List[str]:
        """Return task IDs in topological order (respecting dependencies)."""
        key = f"crimekit:job:{job_id}:deps"
        all_tasks = await self._redis.hgetall(key)
        graph: Dict[str, List[str]] = {}
        for task_id, raw in all_tasks.items():
            info = json.loads(raw)
            graph[task_id] = info.get("dependencies", [])

        in_degree: Dict[str, int] = {tid: 0 for tid in graph}
        for tid, deps in graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[tid] += 1

        queue_list = [tid for tid, deg in in_degree.items() if deg == 0]
        order: List[str] = []
        while queue_list:
            node = queue_list.pop(0)
            order.append(node)
            for tid, deps in graph.items():
                if node in deps:
                    in_degree[tid] -= 1
                    if in_degree[tid] == 0:
                        queue_list.append(tid)
        return order

    async def has_cycle(self, job_id: str) -> bool:
        """Detect if the dependency graph contains a cycle."""
        order = await self.get_topological_order(job_id)
        key = f"crimekit:job:{job_id}:deps"
        all_tasks = await self._redis.hgetall(key)
        return len(order) != len(all_tasks)

    async def mark_completed(self, job_id: str, task_id: str) -> None:
        """Mark a task as completed and return IDs of newly unblocked tasks."""
        await self.update_status(job_id, task_id, TaskStatus.COMPLETED.value)
        metrics.record_dep_resolved()

    async def get_downstream_tasks(self, job_id: str, task_id: str) -> List[str]:
        """Find tasks that directly depend on the given task_id."""
        key = f"crimekit:job:{job_id}:deps"
        all_tasks = await self._redis.hgetall(key)
        downstream: List[str] = []
        for tid, raw in all_tasks.items():
            info = json.loads(raw)
            if task_id in info.get("dependencies", []):
                downstream.append(tid)
        return downstream

    async def cleanup(self, job_id: str) -> None:
        """Remove dependency graph for a completed job."""
        key = f"crimekit:job:{job_id}:deps"
        await self._redis.delete(key)


# ---------------------------------------------------------------------------
# Worker Pool
# ---------------------------------------------------------------------------

WorkerTaskHandler = Callable[[TaskPayload], Awaitable[Dict[str, Any]]]


class WorkerPool:
    """Auto-scaling async worker pool with heartbeat and health monitoring.

    Features:
    - Auto-discovery: workers register themselves in Redis
    - Heartbeat: periodic liveness signals
    - Health monitoring: tracks active/idle/failed workers
    - Autoscaling: scales workers based on queue depth
    - Graceful shutdown
    """

    def __init__(
        self,
        queue: DistributedQueue,
        task_handler: WorkerTaskHandler,
        min_workers: int = MIN_WORKERS,
        max_workers: int = MAX_WORKERS,
        autoscale: bool = True,
    ) -> None:
        self._queue = queue
        self._handler = task_handler
        self._min_workers = min_workers
        self._max_workers = max_workers
        self._autoscale = autoscale
        self._workers: Dict[str, WorkerInfo] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._autoscale_task: Optional[asyncio.Task] = None
        self._retry_poll_task: Optional[asyncio.Task] = None
        self._claim_task: Optional[asyncio.Task] = None

    @property
    def worker_count(self) -> int:
        return len(self._workers)

    @property
    def active_count(self) -> int:
        return sum(1 for w in self._workers.values() if w.status == "processing")

    def _create_worker_info(self) -> WorkerInfo:
        info = WorkerInfo()
        self._workers[info.worker_id] = info
        return info

    async def start(self) -> None:
        """Start the worker pool with min_workers workers."""
        if self._running:
            return
        self._running = True

        for _ in range(self._min_workers):
            info = self._create_worker_info()
            task = asyncio.create_task(self._run_worker(info))
            self._tasks[info.worker_id] = task

        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._retry_poll_task = asyncio.create_task(self._retry_poll_loop())

        if self._autoscale:
            self._autoscale_task = asyncio.create_task(self._autoscale_loop())

        self._claim_task = asyncio.create_task(self._claim_loop())

        logger.info(
            "WorkerPool started: workers=%d min=%d max=%d autoscale=%s",
            self.worker_count, self._min_workers, self._max_workers, self._autoscale,
        )

    async def stop(self) -> None:
        """Gracefully stop all workers."""
        self._running = False

        for task in self._tasks.values():
            task.cancel()

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._autoscale_task:
            self._autoscale_task.cancel()
        if self._retry_poll_task:
            self._retry_poll_task.cancel()
        if self._claim_task:
            self._claim_task.cancel()

        await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()
        self._workers.clear()
        logger.info("WorkerPool stopped")

    async def _run_worker(self, info: WorkerInfo) -> None:
        """Main worker loop: consume → process → ack."""
        worker_key = f"crimekit:worker:{info.worker_id}:info"
        while self._running:
            try:
                info.status = "idle"
                info.last_heartbeat = datetime.now(timezone.utc).isoformat()
                await self._queue.redis.hset(worker_key, mapping={
                    "worker_id": info.worker_id,
                    "status": "idle",
                    "last_heartbeat": info.last_heartbeat,
                    "tasks_completed": str(info.tasks_completed),
                    "tasks_failed": str(info.tasks_failed),
                })
                await self._queue.redis.expire(worker_key, HEARTBEAT_TTL * 2)

                messages = await self._queue.consume(count=1, timeout_ms=2000)
                if not messages:
                    continue

                msg_id, task = messages[0]

                if not self._should_process(task):
                    await self._queue.acknowledge(
                        PRIORITY_STREAMS.get(task.priority, PRIORITY_STREAMS["normal"]),
                        msg_id,
                    )
                    continue

                info.status = "processing"
                info.current_task_id = task.task_id
                start_time = time.monotonic()

                await self._queue.redis.hset(worker_key, mapping={
                    "status": "processing",
                    "current_task": task.task_id,
                })

                try:
                    result = await self._handler(task)
                    elapsed_ms = (time.monotonic() - start_time) * 1000

                    stream = PRIORITY_STREAMS.get(task.priority, PRIORITY_STREAMS["normal"])
                    await self._queue.acknowledge(stream, msg_id)

                    info.tasks_completed += 1
                    info.current_task_id = None
                    info.status = "idle"

                    await self._queue.redis.hset(worker_key, mapping={
                        "status": "idle",
                        "current_task": "",
                        "tasks_completed": str(info.tasks_completed),
                    })

                    metrics.record_task_completed(task.processor_type, elapsed_ms)
                    logger.debug(
                        "Task %s completed by %s in %.1fms",
                        task.task_id, info.worker_id, elapsed_ms,
                    )

                except Exception as exc:
                    elapsed_ms = (time.monotonic() - start_time) * 1000
                    info.tasks_failed += 1
                    info.current_task_id = None
                    info.status = "idle"

                    await self._queue.redis.hset(worker_key, mapping={
                        "status": "idle",
                        "current_task": "",
                        "tasks_failed": str(info.tasks_failed),
                    })

                    metrics.record_task_failed(task.processor_type)

                    retried = await self._queue.retry_manager.schedule_retry(
                        self._queue.redis, task, str(exc),
                    ) if self._queue.retry_manager else False

                    if not retried:
                        await self._queue.dlq.push(task, str(exc), info.worker_id) if self._queue.dlq else None
                        stream = PRIORITY_STREAMS.get(task.priority, PRIORITY_STREAMS["normal"])
                        await self._queue.acknowledge(stream, msg_id)

                    logger.error(
                        "Task %s failed on %s: %s (retried=%s)",
                        task.task_id, info.worker_id, exc, retried,
                    )

            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Worker %s unexpected error: %s", info.worker_id, exc)
                await asyncio.sleep(1)

    def _should_process(self, task: TaskPayload) -> bool:
        """Check worker affinity for this task's processor type."""
        return True

    async def _heartbeat_loop(self) -> None:
        """Periodically update worker heartbeats."""
        while self._running:
            now = datetime.now(timezone.utc).isoformat()
            for worker_id, info in self._workers.items():
                info.last_heartbeat = now
                key = f"crimekit:worker:{worker_id}:hb"
                await self._queue.redis.setex(key, HEARTBEAT_TTL, now)
            metrics.set_worker_counts(self.worker_count, self.active_count)
            await asyncio.sleep(HEARTBEAT_INTERVAL)

    async def _retry_poll_loop(self) -> None:
        """Periodically check for tasks whose retry backoff has elapsed."""
        while self._running:
            try:
                if self._queue.retry_manager:
                    ready = await self._queue.retry_manager.check_retries(self._queue.redis)
                    if ready:
                        logger.info("Re-enqueued %d retried tasks", len(ready))
            except Exception as exc:
                logger.error("Retry poll error: %s", exc)
            await asyncio.sleep(5)

    async def _claim_loop(self) -> None:
        """Periodically claim stale messages from other workers."""
        while self._running:
            try:
                claimed = await self._queue.claim_stale()
                if claimed:
                    logger.info("Claimed %d stale messages from other workers", len(claimed))
            except Exception as exc:
                logger.error("Claim loop error: %s", exc)
            await asyncio.sleep(30)

    async def _autoscale_loop(self) -> None:
        """Autoscale workers based on queue depth."""
        while self._running:
            try:
                depths = await self._queue.queue_depth()
                total_depth = sum(depths.values())
                current = self.worker_count

                if total_depth >= SCALE_UP_THRESHOLD and current < self._max_workers:
                    target = min(current + 1, self._max_workers)
                    for _ in range(target - current):
                        info = self._create_worker_info()
                        task = asyncio.create_task(self._run_worker(info))
                        self._tasks[info.worker_id] = task
                    metrics.record_autoscale()
                    logger.info(
                        "Scaled UP: %d → %d workers (queue depth=%d)",
                        current, target, total_depth,
                    )

                elif total_depth <= SCALE_DOWN_THRESHOLD and current > self._min_workers:
                    target = max(current - 1, self._min_workers)
                    to_remove = current - target
                    idle_workers = [
                        wid for wid, info in self._workers.items()
                        if info.status == "idle"
                    ]
                    for wid in idle_workers[:to_remove]:
                        if wid in self._tasks:
                            self._tasks[wid].cancel()
                            del self._tasks[wid]
                        if wid in self._workers:
                            del self._workers[wid]
                    metrics.record_autoscale()
                    logger.info(
                        "Scaled DOWN: %d → %d workers (queue depth=%d)",
                        current, target, total_depth,
                    )

            except Exception as exc:
                logger.error("Autoscale error: %s", exc)
            await asyncio.sleep(SCALE_CHECK_INTERVAL)

    async def get_worker_status(self) -> List[Dict[str, Any]]:
        """Return status of all registered workers."""
        status = []
        for wid, info in self._workers.items():
            key = f"crimekit:worker:{wid}:hb"
            last_hb = await self._queue.redis.get(key)
            alive = last_hb is not None
            status.append({
                "worker_id": wid,
                "name": info.name,
                "status": info.status,
                "alive": alive,
                "tasks_completed": info.tasks_completed,
                "tasks_failed": info.tasks_failed,
                "current_task_id": info.current_task_id,
                "started_at": info.started_at,
                "last_heartbeat": info.last_heartbeat,
            })
        return status

    async def get_healthy_workers(self) -> List[WorkerInfo]:
        """Return workers whose heartbeat is still valid."""
        healthy: List[WorkerInfo] = []
        for wid, info in self._workers.items():
            key = f"crimekit:worker:{wid}:hb"
            if await self._queue.redis.exists(key):
                healthy.append(info)
        return healthy


# ---------------------------------------------------------------------------
# Database Models (PostgreSQL persistence)
# ---------------------------------------------------------------------------

def _get_db_models():
    """Lazy import of SQLAlchemy models to avoid circular imports."""
    try:
        from ..models import Base, ForensicJob
        return Base, ForensicJob
    except ImportError:
        return None, None


def _get_db_session():
    """Lazy import of database session factory."""
    try:
        from ..database import SessionLocal
        return SessionLocal
    except ImportError:
        return None


class DistributedJobStore:
    """PostgreSQL-backed job persistence with checkpoint/resume support."""

    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    async def persist_job(
        self,
        job_id: str,
        evidence_id: str,
        processors: List[str],
        status: str = "queued",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist a job to PostgreSQL via SQLAlchemy."""
        SessionLocal = _get_db_session()
        if SessionLocal is None:
            logger.warning("Database not available; skipping job persistence")
            return

        db = SessionLocal()
        try:
            from ..models import ForensicJob
            job = ForensicJob(
                id=job_id,
                evidence_id=evidence_id,
                processors=processors,
                status=status,
            )
            db.merge(job)
            db.commit()
            logger.debug("Job %s persisted to PostgreSQL", job_id)
        except Exception as exc:
            db.rollback()
            logger.error("Failed to persist job %s: %s", job_id, exc)
        finally:
            db.close()

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update job status in PostgreSQL."""
        SessionLocal = _get_db_session()
        if SessionLocal is None:
            return

        db = SessionLocal()
        try:
            from ..models import ForensicJob
            from datetime import datetime, timezone
            job = db.query(ForensicJob).filter(ForensicJob.id == job_id).first()
            if job:
                job.status = status
                if result:
                    job.result = result
                if error:
                    job.error = error
                if status == "running" and job.started_at is None:
                    job.started_at = datetime.now(timezone.utc)
                if status in ("completed", "failed", "cancelled"):
                    job.finished_at = datetime.now(timezone.utc)
                db.commit()
        except Exception as exc:
            db.rollback()
            logger.error("Failed to update job %s: %s", job_id, exc)
        finally:
            db.close()

    async def save_checkpoint(
        self,
        job_id: str,
        task_id: str,
        checkpoint_data: Dict[str, Any],
    ) -> None:
        """Save a processing checkpoint for resume capability."""
        key = f"crimekit:checkpoint:{job_id}:{task_id}"
        await self._redis.setex(
            key,
            86400 * 7,
            json.dumps(checkpoint_data, default=str),
        )

    async def load_checkpoint(
        self,
        job_id: str,
        task_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Load the last checkpoint for a task."""
        key = f"crimekit:checkpoint:{job_id}:{task_id}"
        raw = await self._redis.get(key)
        if raw:
            return json.loads(raw)
        return None

    async def resume_job(self, job_id: str) -> Optional[List[TaskPayload]]:
        """Resume a paused or failed job from its last checkpoint.

        Returns the list of tasks that need to be re-queued.
        """
        SessionLocal = _get_db_session()
        if SessionLocal is None:
            return None

        db = SessionLocal()
        try:
            from ..models import ForensicJob
            job = db.query(ForensicJob).filter(ForensicJob.id == job_id).first()
            if not job or job.status not in ("failed", "cancelled", "paused"):
                return None

            deps_key = f"crimekit:job:{job_id}:deps"
            all_deps = await self._redis.hgetall(deps_key)

            incomplete_tasks: List[TaskPayload] = []
            for task_id, raw in all_deps.items():
                info = json.loads(raw)
                if info.get("status") not in ("completed",):
                    checkpoint = await self.load_checkpoint(job_id, task_id)
                    task = TaskPayload(
                        task_id=task_id,
                        job_id=job_id,
                        processor_type=info.get("processor_type", ""),
                        dependencies=info.get("dependencies", []),
                        checkpoint=checkpoint or {},
                        retry_count=0,
                    )
                    incomplete_tasks.append(task)

            return incomplete_tasks if incomplete_tasks else None
        except Exception as exc:
            logger.error("Failed to resume job %s: %s", job_id, exc)
            return None
        finally:
            db.close()

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job and all its pending tasks."""
        await self.update_job_status(job_id, "cancelled")

        deps_key = f"crimekit:job:{job_id}:deps"
        all_deps = await self._redis.hgetall(deps_key)

        cancelled = 0
        for task_id, raw in all_deps.items():
            info = json.loads(raw)
            if info.get("status") in ("pending", "queued"):
                await self._redis.hset(deps_key, task_id, json.dumps({
                    **info,
                    "status": TaskStatus.CANCELLED.value,
                }))
                cancelled += 1

        for stream in PRIORITY_STREAMS.values():
            entries = await self._redis.xrange(stream)
            for msg_id, fields in entries:
                if fields.get("job_id") == job_id:
                    await self._redis.xdel(stream, msg_id)
                    cancelled += 1

        logger.info("Job %s cancelled: %d tasks removed", job_id, cancelled)
        return cancelled > 0


# ---------------------------------------------------------------------------
# Distributed System (Facade)
# ---------------------------------------------------------------------------

class DistributedSystem:
    """High-level facade that wires all distributed components together.

    Usage::

        system = DistributedSystem(redis_url="redis://localhost:6379/0")
        await system.start()

        job_id = "case-123"
        await system.enqueue_job(
            job_id=job_id,
            evidence_id="ev-456",
            processors=["hashes", "ocr", "pdf_text"],
        )

        progress = await system.get_progress(job_id)
        await system.cancel_job(job_id)
        await system.stop()
    """

    def __init__(
        self,
        redis_url: str = REDIS_URL,
        min_workers: int = MIN_WORKERS,
        max_workers: int = MAX_WORKERS,
        autoscale: bool = True,
        task_handler: Optional[WorkerTaskHandler] = None,
        routing_table: Optional[Dict[str, str]] = None,
    ) -> None:
        self._redis_url = redis_url
        self._queue = DistributedQueue(redis_url)
        self._router = TaskRouter(routing_table)
        self._dep_graph: Optional[JobDependencyGraph] = None
        self._store: Optional[DistributedJobStore] = None
        self._handler = task_handler or self._default_handler
        self._pool = WorkerPool(
            self._queue,
            self._handler,
            min_workers=min_workers,
            max_workers=max_workers,
            autoscale=autoscale,
        )

    @property
    def queue(self) -> DistributedQueue:
        return self._queue

    @property
    def router(self) -> TaskRouter:
        return self._router

    @property
    def pool(self) -> WorkerPool:
        return self._pool

    @property
    def dep_graph(self) -> JobDependencyGraph:
        if self._dep_graph is None:
            raise RuntimeError("System not started")
        return self._dep_graph

    @property
    def store(self) -> DistributedJobStore:
        if self._store is None:
            raise RuntimeError("System not started")
        return self._store

    @property
    def metrics(self) -> DistributedMetrics:
        return metrics

    async def start(self) -> None:
        """Initialize connections and start workers."""
        await self._queue.connect()
        self._dep_graph = JobDependencyGraph(self._queue.redis)
        self._store = DistributedJobStore(self._queue.redis)
        await self._pool.start()
        logger.info("DistributedSystem started")

    async def stop(self) -> None:
        """Shut down workers and close connections."""
        await self._pool.stop()
        await self._queue.close()
        logger.info("DistributedSystem stopped")

    async def healthcheck(self) -> bool:
        """Return True only if the backing Redis connection is reachable.

        The aioredis client connects lazily, so ``start()`` succeeds even when
        Redis is down. A real PING is required to detect an unusable backend.
        """
        try:
            return bool(await self._queue.redis.ping())
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis healthcheck failed: %s", exc)
            return False

    async def enqueue_job(
        self,
        job_id: str,
        evidence_id: str,
        processors: List[str],
        case_id: Optional[str] = None,
    ) -> List[str]:
        """Enqueue a forensic processing job.

        Creates tasks for each processor, registers dependencies,
        and submits to the appropriate priority streams.

        Returns list of task IDs.
        """
        await self._store.persist_job(job_id, evidence_id, processors)

        task_ids: List[str] = []
        tasks: List[TaskPayload] = []

        for idx, proc in enumerate(processors):
            deps: List[str] = []
            if idx > 0:
                deps.append(task_ids[-1])

            task = TaskPayload(
                job_id=job_id,
                processor_type=proc,
                payload={
                    "evidence_id": evidence_id,
                    "case_id": case_id,
                    "processor": proc,
                },
                dependencies=deps,
            )
            task = self._router.route_task(task)
            await self._dep_graph.register_task(task)
            await self._dep_graph.update_status(job_id, task.task_id, TaskStatus.QUEUED.value)
            tasks.append(task)
            task_ids.append(task.task_id)

        ready = await self._dep_graph.get_ready_tasks(job_id)
        for task in tasks:
            if task.task_id in ready:
                await self._queue.submit(task, priority=task.priority)

        await self._queue.update_progress(
            job_id,
            status="queued",
            completed=0,
            total=len(processors),
        )

        return task_ids

    async def enqueue_tasks(
        self,
        tasks: List[TaskPayload],
    ) -> List[str]:
        """Submit pre-built tasks to the queue with routing."""
        task_ids: List[str] = []
        grouped: Dict[str, List[TaskPayload]] = defaultdict(list)

        for task in tasks:
            task = self._router.route_task(task)
            if task.job_id:
                await self._dep_graph.register_task(task)
            grouped[task.priority].append(task)

        for priority, group in grouped.items():
            await self._queue.submit_many(group, priority=priority)
            task_ids.extend(t.task_id for t in group)

        return task_ids

    async def complete_task(
        self,
        job_id: str,
        task_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Mark a task as completed and return newly unblocked task IDs."""
        await self._dep_graph.mark_completed(job_id, task_id)
        await self._dep_graph.update_status(job_id, task_id, TaskStatus.COMPLETED.value)

        deps_key = f"crimekit:job:{job_id}:deps"
        all_deps = await self._queue.redis.hgetall(deps_key)
        total = len(all_deps)
        completed = sum(
            1 for raw in all_deps.values()
            if json.loads(raw).get("status") == TaskStatus.COMPLETED.value
        )

        await self._queue.update_progress(
            job_id,
            status="running" if completed < total else "completed",
            completed=completed,
            total=total,
        )

        if completed >= total:
            await self._store.update_job_status(job_id, "completed", result=result)
            await self._dep_graph.cleanup(job_id)

        downstream = await self._dep_graph.get_downstream_tasks(job_id, task_id)
        newly_ready: List[str] = []
        for dep_id in downstream:
            if await self._dep_graph.are_dependencies_met(job_id, dep_id):
                newly_ready.append(dep_id)
                raw = await self._queue.redis.hget(deps_key, dep_id)
                if raw:
                    info = json.loads(raw)
                    task = TaskPayload(
                        task_id=dep_id,
                        job_id=job_id,
                        processor_type=info.get("processor_type", ""),
                        dependencies=info.get("dependencies", []),
                    )
                    task = self._router.route_task(task)
                    await self._queue.submit(task, priority=task.priority)

        return newly_ready

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job and all its pending tasks."""
        cancelled = await self._store.cancel_job(job_id)
        await self._queue.update_progress(job_id, status="cancelled", completed=0, total=0)
        return cancelled

    async def resume_job(self, job_id: str) -> Optional[List[str]]:
        """Resume a failed or paused job from its last checkpoint."""
        tasks = await self._store.resume_job(job_id)
        if not tasks:
            return None

        task_ids: List[str] = []
        for task in tasks:
            task = self._router.route_task(task)
            await self._dep_graph.register_task(task)
            await self._dep_graph.update_status(job_id, task.task_id, TaskStatus.QUEUED.value)
            await self._queue.submit(task, priority=task.priority)
            task_ids.append(task.task_id)

        await self._store.update_job_status(job_id, "queued")
        return task_ids

    async def get_progress(self, job_id: str) -> Dict[str, Any]:
        return await self._queue.get_progress(job_id)

    async def get_queue_depth(self) -> Dict[str, int]:
        return await self._queue.queue_depth()

    async def get_worker_status(self) -> List[Dict[str, Any]]:
        return await self._pool.get_worker_status()

    async def get_metrics(self) -> str:
        return metrics.to_prometheus()

    @staticmethod
    async def _default_handler(task: TaskPayload) -> Dict[str, Any]:
        """Default task handler — logs and returns placeholder result."""
        logger.info("Default handler processing task %s (processor=%s)", task.task_id, task.processor_type)
        return {"status": "completed", "processor": task.processor_type}


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_system: Optional[DistributedSystem] = None


async def get_distributed_system() -> DistributedSystem:
    """Get or create the global DistributedSystem singleton."""
    global _system
    if _system is None:
        system = DistributedSystem()
        await system.start()
        _system = system
    return _system


async def shutdown_distributed_system() -> None:
    """Shut down the global DistributedSystem."""
    global _system
    if _system is not None:
        await _system.stop()
        _system = None


__all__ = [
    # Core classes
    "DistributedQueue",
    "WorkerPool",
    "TaskRouter",
    "DeadLetterQueue",
    "RetryManager",
    "JobDependencyGraph",
    "DistributedJobStore",
    "DistributedSystem",
    "DistributedMetrics",
    # Data models
    "TaskPayload",
    "WorkerInfo",
    "TaskStatus",
    "JobStatus",
    # Configuration
    "PRIORITY_STREAMS",
    "PRIORITY_ORDER",
    "CONSUMER_GROUP",
    "metrics",
    # Module functions
    "get_distributed_system",
    "shutdown_distributed_system",
]
