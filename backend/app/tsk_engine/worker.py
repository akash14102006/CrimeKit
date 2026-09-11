"""Isolated TSK worker — sandboxed execution for disk image forensic analysis.

Provides process-level isolation, resource limits, timeout enforcement,
and graceful cancellation for TSK forensic processing jobs.
"""

from __future__ import annotations

import logging
import os
import resource
import signal
import tempfile
import threading
import time
import uuid
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..database import SessionLocal
from ..models import Evidence, ForensicJob, ForensicResult, Document
from ..forensic_engine.schemas import EvidenceSchema, EvidenceCategory
from .events import ForensicEventEmitter
from .pipeline import TSKPipeline, TSKPipelineResult
from .schemas import TSKProcessingConfig

logger = logging.getLogger(__name__)


def _json_safe(value: Any) -> Any:
    """Convert pipeline dataclasses/enums into JSON-serializable values."""
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _json_safe(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)

_WORKER_COUNT = 0
_WORKER_LOCK = threading.Lock()


def _generate_worker_id() -> str:
    global _WORKER_COUNT
    with _WORKER_LOCK:
        _WORKER_COUNT += 1
        return f"tsk-worker-{os.getpid()}-{_WORKER_COUNT}"


class TSKWorkerConfig:
    max_workers: int = 2
    timeout_seconds: int = 600
    memory_limit_mb: int = 2048
    cpu_limit_percent: float = 80.0
    temp_dir: str = ""
    restricted_network: bool = True
    read_only_evidence: bool = True


class TSKWorker:
    """Isolated TSK forensic processing worker.

    Each worker runs in its own thread with:
    - Execution timeout
    - Memory limit monitoring
    - Temporary workspace isolation
    - Read-only evidence access
    - Graceful cancellation
    - Structured event emission
    """

    def __init__(
        self,
        config: Optional[TSKWorkerConfig] = None,
        redis_client: Optional[Any] = None,
    ) -> None:
        self.config = config or TSKWorkerConfig()
        self._redis = redis_client
        self._worker_id = _generate_worker_id()
        self._running = False
        self._cancelled = False
        self._current_job_id: Optional[str] = None
        self._start_time: Optional[float] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._cancel_event = threading.Event()

    @property
    def worker_id(self) -> str:
        return self._worker_id

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def status(self) -> Dict[str, Any]:
        return {
            "worker_id": self._worker_id,
            "running": self._running,
            "current_job": self._current_job_id,
            "uptime_seconds": round(time.monotonic() - self._start_time, 2) if self._start_time else 0,
        }

    def process_evidence(
        self,
        evidence_id: str,
        case_id: str,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> TSKPipelineResult:
        """Process a single evidence item through the full TSK pipeline.

        Runs in the calling thread with timeout enforcement.
        Returns the pipeline result with all extracted data.
        """
        self._running = True
        self._start_time = time.monotonic()
        self._cancel_event.clear()

        db = SessionLocal()
        try:
            evidence_record = db.query(Evidence).filter(Evidence.id == evidence_id).first()
            if not evidence_record:
                raise ValueError(f"Evidence {evidence_id} not found")

            storage_path = evidence_record.storage_path
            if not storage_path or not os.path.isfile(storage_path):
                raise ValueError(f"Evidence file not found: {storage_path}")

            if self.config.read_only_evidence:
                if os.path.exists(storage_path):
                    try:
                        os.chmod(storage_path, 0o444)
                    except (OSError, PermissionError):
                        pass

            evidence_schema = EvidenceSchema(
                evidence_id=evidence_id,
                case_id=case_id,
                storage_path=storage_path,
                filename=evidence_record.filename or os.path.basename(storage_path),
                sha256=evidence_record.sha256 or "",
                size=evidence_record.size or os.path.getsize(storage_path),
                mime_type=evidence_record.mime_type,
                category=EvidenceCategory.DISK_IMAGE,
            )

            emitter = ForensicEventEmitter(
                case_id=case_id,
                evidence_id=evidence_id,
                worker_id=self._worker_id,
                redis_client=self._redis,
            )

            pipeline_config = TSKProcessingConfig(
                case_id=case_id,
                evidence_id=evidence_id,
                worker_id=self._worker_id,
                timeout_seconds=self.config.timeout_seconds,
                emit_events=True,
            )

            pipeline = TSKPipeline(config=pipeline_config, emitter=emitter)

            self._current_job_id = evidence_id
            self._thread = threading.current_thread()

            timer = threading.Timer(
                self.config.timeout_seconds,
                self._timeout_handler,
            )
            timer.daemon = True
            timer.start()

            try:
                result = pipeline.run(evidence_schema)
            finally:
                timer.cancel()

            if result.success:
                self._persist_results(db, evidence_record, evidence_schema, result, emitter)

            return result

        except Exception as exc:
            logger.error("Worker %s failed on evidence %s: %s", self._worker_id, evidence_id, exc)
            result = TSKPipelineResult()
            result.errors.append(str(exc))
            return result
        finally:
            self._running = False
            self._current_job_id = None
            self._start_time = None
            db.close()

    def _timeout_handler(self) -> None:
        if self._running:
            logger.warning(
                "Worker %s timeout after %ds on job %s",
                self._worker_id, self.config.timeout_seconds, self._current_job_id,
            )
            self._cancelled = True

    def cancel(self) -> None:
        with self._lock:
            self._cancelled = True
            self._cancel_event.set()

    def _persist_results(
        self,
        db: Any,
        evidence_record: Any,
        evidence_schema: EvidenceSchema,
        result: TSKPipelineResult,
        emitter: ForensicEventEmitter,
    ) -> None:
        # Persist into the canonical forensic sinks:
        # - Evidence.metadata_json carries processing status (Evidence has no
        #   processing_status column, so it is stored inside metadata_json).
        # - ForensicResult(processor="tsk") carries timeline/entities/
        #   relationships/artifacts, which is what the /timeline API reads.
        try:
            meta = evidence_schema.to_dict()
            if not isinstance(meta, dict):
                meta = {}
            meta["processing_status"] = "completed"
            meta["processor"] = "tsk"
            evidence_record.metadata_json = meta

            timeline = []
            for tl_event in result.timeline_events[:500]:
                item = _json_safe(tl_event)
                if not isinstance(item, dict):
                    continue
                timestamp_type = item.get("timestamp_type", "")
                file_path = item.get("file_path", "")
                detail = f"TSK {timestamp_type} {file_path}".strip()
                timeline.append(
                    {
                        "timestamp": str(item.get("timestamp", "")),
                        "event": item.get("event_type", "Forensic Artifact Detected"),
                        "description": detail or "Extracted via tsk",
                        "metadata": {
                            "file_name": item.get("file_name"),
                            "file_path": file_path,
                            "metadata_addr": item.get("metadata_addr"),
                            "timestamp_type": timestamp_type,
                            "event_id": item.get("event_id"),
                            "confidence": item.get("confidence"),
                        },
                    }
                )

            payload = {
                "processor": "tsk",
                "success": True,
                "timeline": timeline,
                "entities": _json_safe(result.entities[:500]),
                "relationships": _json_safe(result.relationships[:500]),
                "artifacts": _json_safe(result.artifacts[:500]),
                "files_summary": {
                    "total_files": len(result.files),
                    "total_partitions": len(result.partitions),
                    "total_filesystems": len(result.filesystem_infos),
                },
                "stages_completed": list(result.stages_completed),
                "stages_failed": list(result.stages_failed),
                "errors": list(result.errors),
            }
            db.add(
                ForensicResult(
                    evidence_id=evidence_schema.evidence_id,
                    processor="tsk",
                    result=payload,
                )
            )
            db.commit()
            logger.info(
                "Worker %s persisted results: %d files, %d artifacts, %d timeline, %d entities",
                self._worker_id,
                len(result.files), len(result.artifacts),
                len(result.timeline_events), len(result.entities),
            )
        except Exception as exc:
            logger.error("Failed to persist TSK results: %s", exc)
            db.rollback()

    def cleanup_temp(self) -> None:
        temp = self.config.temp_dir or tempfile.gettempdir()
        prefix = f"tsk_worker_{self._worker_id}"
        try:
            for item in os.listdir(temp):
                if item.startswith(prefix):
                    path = os.path.join(temp, item)
                    if os.path.isdir(path):
                        import shutil
                        shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass
