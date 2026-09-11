"""Distributed processing system API routes.

Provides endpoints for task management, worker monitoring,
queue inspection, and dead-letter queue operations.
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import database, models
from .auth import get_current_user
from .database import SessionLocal
from .distributed import get_distributed_system, DistributedSystem, TaskPayload, TaskStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/distributed", tags=["distributed"])


def _require_admin_or_investigator(current_user: models.User):
    roles = [r.name for r in current_user.roles]
    if "admin" not in roles and "investigator" not in roles:
        raise HTTPException(status_code=403, detail="forbidden: admin or investigator required")


# ── Request / response schemas ──────────────────────────────────────────

class EnqueueTaskIn(BaseModel):
    processor_type: str
    payload: Dict[str, Any] = {}
    priority: int = 5
    dependencies: List[str] = []


class EnqueueBatchIn(BaseModel):
    tasks: List[EnqueueTaskIn]


class TaskActionResponse(BaseModel):
    detail: str
    task_id: str


class JobActionResponse(BaseModel):
    detail: str
    job_id: str


# ── Helpers ──────────────────────────────────────────────────────────────

async def _get_ds() -> Optional[DistributedSystem]:
    """Get the distributed system, returning None if Redis is unavailable.

    The aioredis client connects lazily, so a successful ``start()`` does not
    guarantee Redis is reachable. We PING to confirm real connectivity before
    handing the system to a route; otherwise we return ``None`` so the route
    can respond with 503 instead of serving fake/degraded data.
    """
    try:
        ds = await get_distributed_system()
        if not await ds.healthcheck():
            return None
        return ds
    except Exception as exc:  # noqa: BLE001
        logger.warning("Distributed system unavailable: %s", exc)
        return None


def _require_ds(ds: Optional[DistributedSystem]) -> DistributedSystem:
    """Raise 503 if the distributed system is not available."""
    if ds is None:
        raise HTTPException(
            status_code=503,
            detail="Distributed processing service is unavailable. Redis may not be running.",
        )
    return ds


# ── 0. GET /health ─────────────────────────────────────────────────────

@router.get("/health")
async def distributed_health() -> Dict[str, Any]:
    """Expose the distributed subsystem health without requiring auth.

    Returns a 200 with a ``status`` of ``healthy`` (Redis reachable) or
    ``degraded`` (Redis unreachable) so monitoring and the UI can show a
    useful state instead of a bare 500/503.
    """
    ds = await _get_ds_unauthed()
    if ds is None:
        return {
            "status": "degraded",
            "redis_reachable": False,
            "detail": "Redis is not reachable. Distributed processing is unavailable.",
        }
    try:
        workers = await ds.get_worker_status()
    except Exception:
        workers = []
    return {
        "status": "healthy",
        "redis_reachable": True,
        "workers_registered": len(workers),
        "detail": "Distributed processing subsystem is operational.",
    }


async def _get_ds_unauthed() -> Optional[DistributedSystem]:
    """Healthcheck variant that does not depend on an authenticated user."""
    try:
        ds = await get_distributed_system()
        if not await ds.healthcheck():
            return None
        return ds
    except Exception as exc:  # noqa: BLE001
        logger.warning("Distributed system unavailable: %s", exc)
        return None


# ── 1. POST /tasks ──────────────────────────────────────────────────────

@router.post("/tasks", status_code=201)
async def enqueue_task(
    body: EnqueueTaskIn,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Enqueue a single task for distributed processing."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    task_payload = TaskPayload(
        processor_type=body.processor_type,
        payload=body.payload,
        priority=body.priority,
        dependencies=body.dependencies,
        created_by=current_user.id,
    )
    tasks = await ds.enqueue_tasks([task_payload])
    task = tasks[0] if tasks else None
    if task is None:
        raise HTTPException(status_code=500, detail="failed to enqueue task")
    return {"detail": "task enqueued", "task_id": task.id}


# ── 2. POST /tasks/batch ───────────────────────────────────────────────

@router.post("/tasks/batch", status_code=201)
async def enqueue_batch(
    body: EnqueueBatchIn,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Enqueue multiple tasks at once."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    payloads = [
        TaskPayload(
            processor_type=t.processor_type,
            payload=t.payload,
            priority=t.priority,
            dependencies=t.dependencies,
            created_by=current_user.id,
        )
        for t in body.tasks
    ]
    tasks = await ds.enqueue_tasks(payloads)
    return {"detail": "batch enqueued", "task_ids": [t.id for t in tasks], "count": len(tasks)}


# ── 3. GET /tasks/{task_id}/progress ───────────────────────────────────

@router.get("/tasks/{task_id}/progress")
async def get_task_progress(
    task_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Get the progress and status of a specific task."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    progress = await ds.get_progress(task_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="task not found")
    return progress


# ── 4. POST /tasks/{task_id}/cancel ───────────────────────────────────

@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Cancel a pending or in-progress task."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    result = await ds.cancel_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="task not found or cannot be cancelled")
    return {"detail": "task cancelled", "task_id": task_id}


# ── 5. POST /tasks/{task_id}/retry ────────────────────────────────────

@router.post("/tasks/{task_id}/retry")
async def retry_task(
    task_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Retry a previously failed task."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    try:
        result = await ds.cancel_task(task_id)
    except Exception:
        result = False
    if not result:
        raise HTTPException(status_code=404, detail="task not found or not in a retryable state")
    return {"detail": "task re-enqueued", "task_id": task_id}


# ── 6. GET /jobs/{job_id} ─────────────────────────────────────────────

@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Get the status and progress of a job (collection of tasks)."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    job = await ds.get_progress(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


# ── 7. POST /jobs/{job_id}/cancel ─────────────────────────────────────

@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Cancel all tasks belonging to a job."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    result = await ds.cancel_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="job not found or cannot be cancelled")
    return {"detail": "job cancelled", "job_id": job_id}


# ── 8. POST /jobs/{job_id}/resume ─────────────────────────────────────

@router.post("/jobs/{job_id}/resume")
async def resume_job(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Resume a failed job by re-enqueuing its incomplete tasks."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    result = await ds.resume_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="job not found or not in a resumable state")
    return {"detail": "job resumed", "job_id": job_id}


# ── 9. GET /queue/depth ───────────────────────────────────────────────

@router.get("/queue/depth")
async def get_queue_depth(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Get the current queue depth broken down by priority level."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    depth = await ds.get_queue_depth()
    return depth


# ── 10. GET /workers ──────────────────────────────────────────────────

@router.get("/workers")
async def list_workers(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Get the status of all registered workers."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    workers = await ds.get_worker_status()
    return {"workers": workers, "total": len(workers)}


# ── 11. GET /workers/{worker_id} ──────────────────────────────────────

@router.get("/workers/{worker_id}")
async def get_worker(
    worker_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Get the status of a specific worker by ID."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    workers = await ds.get_worker_status()
    worker = next((w for w in workers if w.get("worker_id") == worker_id), None)
    if worker is None:
        raise HTTPException(status_code=404, detail="worker not found")
    return worker


# ── 12. GET /metrics ──────────────────────────────────────────────────

@router.get("/metrics")
async def get_metrics(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Get Prometheus-format metrics for the distributed processing system."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    metrics = await ds.get_metrics()
    if isinstance(metrics, str):
        return {"raw_metrics": metrics}
    return metrics


# ── 13. GET /dlq ──────────────────────────────────────────────────────

@router.get("/dlq")
async def list_dlq(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """List items currently in the dead-letter queue."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    items = await ds._queue.dlq.peek() if ds._queue.dlq else []
    return {"items": items, "total": len(items)}


# ── 14. POST /dlq/{task_id}/replay ────────────────────────────────────

@router.post("/dlq/{task_id}/replay")
async def replay_dlq_task(
    task_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Replay a task from the dead-letter queue by re-enqueuing it."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    result = await ds._queue.dlq.replay(task_id) if ds._queue.dlq else False
    if not result:
        raise HTTPException(status_code=404, detail="task not found in DLQ")
    return {"detail": "task replayed", "task_id": task_id}


# ── 15. DELETE /dlq ───────────────────────────────────────────────────

@router.delete("/dlq")
async def purge_dlq(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db_session),
):
    """Purge all items from the dead-letter queue."""
    _require_admin_or_investigator(current_user)
    ds = _require_ds(await _get_ds())
    count = await ds._queue.dlq.purge() if ds._queue.dlq else 0
    return {"detail": "DLQ purged", "purged_count": count}
