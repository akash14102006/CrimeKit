"""TSK integration layer — connects TSK pipeline to CrimeKit infrastructure.

Bridges the TSK forensic pipeline with:
- Processing queue (enqueue TSK jobs)
- Neo4j graph (persist forensic entities/relationships)
- Elasticsearch (index searchable artifacts)
- Timeline engine (merge filesystem temporal data)
- WebSocket/SSE (real-time event relay)
- AI pipeline (route extractable content)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ..database import SessionLocal
from ..models import Evidence, ForensicJob
from ..forensic_engine.schemas import EvidenceSchema, EvidenceCategory
from .events import ForensicEventEmitter
from .pipeline import TSKPipeline, TSKPipelineResult
from .schemas import TSKProcessingConfig

logger = logging.getLogger(__name__)


def _json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


class TSKIntegration:
    """High-level integration facade for TSK forensic processing.

    Provides methods to:
    - Enqueue evidence for TSK processing
    - Process evidence directly
    - Query processing results
    - Stream real-time events
    """

    def __init__(self, redis_client: Optional[Any] = None) -> None:
        self._redis = redis_client

    def enqueue_tsk_processing(
        self,
        evidence_id: str,
        case_id: str,
        priority: str = "high",
    ) -> Dict[str, Any]:
        """Enqueue evidence for asynchronous TSK processing."""
        db = SessionLocal()
        try:
            evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
            if not evidence:
                return {"error": f"Evidence {evidence_id} not found"}

            job = ForensicJob(
                evidence_id=evidence_id,
                processors=["tsk"],
                status="queued",
            )
            db.add(job)
            db.commit()

            if self._redis:
                stream = f"crimekit:tasks:{priority}"
                self._redis.xadd(stream, {
                    "job_id": str(job.id),
                    "evidence_id": evidence_id,
                    "case_id": case_id,
                    "processor": "tsk",
                })

            return {
                "job_id": str(job.id),
                "status": "queued",
                "processor": "tsk",
                "evidence_id": evidence_id,
                "case_id": case_id,
            }
        except Exception as exc:
            db.rollback()
            logger.error("Failed to enqueue TSK job: %s", exc)
            return {"error": str(exc)}
        finally:
            db.close()

    def process_evidence_sync(
        self,
        evidence_id: str,
        case_id: str,
    ) -> Dict[str, Any]:
        """Process evidence synchronously through the full TSK pipeline."""
        from .worker import TSKWorker

        worker = TSKWorker(redis_client=self._redis)
        try:
            result = worker.process_evidence(evidence_id=evidence_id, case_id=case_id)
            metrics = {
                "total_partitions": len(result.partitions),
                "total_filesystems": len(result.filesystem_infos),
                "total_files": len(result.files),
                "total_directories": sum(1 for item in result.files if item.object_type.value == "directory"),
                "total_deleted": sum(1 for item in result.files if item.is_deleted),
                "total_unallocated": sum(1 for item in result.files if item.allocation_state.value == "unallocated"),
                "total_orphan": sum(1 for item in result.files if item.allocation_state.value == "orphan"),
                "total_size_bytes": sum(item.size for item in result.files),
                "artifacts_extracted": len(result.artifacts),
                "timeline_events": len(result.timeline_events),
                "processing_time_ms": round(result.total_duration * 1000),
            }
            payload = {
                "job_id": evidence_id,
                "success": result.success,
                "status": "completed" if result.success else "failed",
                "image_info": _json_value(result.image_info),
                "volume_info": _json_value(result.volume_info),
                "filesystems": _json_value(result.filesystem_infos),
                "files": _json_value(result.files),
                "artifacts": _json_value(result.artifacts),
                "timeline": _json_value(result.timeline_events),
                "metrics": metrics,
                "timeline_events": len(result.timeline_events),
                "entities": len(result.entities),
                "relationships": len(result.relationships),
                "entities_data": _json_value(result.entities),
                "relationships_data": _json_value(result.relationships),
                "stages_completed": len(result.stages_completed),
                "stages_failed": len(result.stages_failed),
                "stages": _json_value(result.stages_completed),
                "errors": result.errors,
                "duration_seconds": result.total_duration,
                "event_log": worker._thread and [],
            }
            return payload
        finally:
            worker.cleanup_temp()

    def get_tsk_capabilities(self) -> Dict[str, Any]:
        """Return TSK engine capabilities and supported formats."""
        from .bindings import TSKBindings
        ewf = TSKBindings.ewf_capability()

        tsk_available = TSKBindings.is_available()
        supported_formats = [f.value for f in TSKBindings.supported_image_formats()]
        return {
            "tsk_available": tsk_available,
            "pytsk_available": tsk_available,
            "tsk_version": "native" if tsk_available else None,
            "libewf_available": ewf["supported"],
            "ewf": ewf,
            "supported_formats": supported_formats,
            "supported_image_formats": supported_formats,
            "supported_filesystems": [
                "ntfs", "fat12", "fat16", "fat32", "exfat",
                "ext2", "ext3", "ext4", "hfs", "apfs",
                "iso9660", "ufs", "yaffs2",
            ],
            "features": {
                "partition_detection": True,
                "filesystem_detection": True,
                "file_enumeration": True,
                "metadata_extraction": True,
                "allocation_classification": True,
                "deleted_file_detection": True,
                "timeline_extraction": True,
                "content_reading": True,
                "artifact_normalization": True,
            },
        }

    def get_processing_status(self, job_id: str) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            job = db.query(ForensicJob).filter(ForensicJob.id == job_id).first()
            if not job:
                return {"error": f"Job {job_id} not found"}
            evidence = (
                db.query(Evidence).filter(Evidence.id == job.evidence_id).first()
                if job.evidence_id
                else None
            )
            processors = job.processors or []
            return {
                "job_id": str(job.id),
                "status": job.status,
                "processor": processors[0] if processors else None,
                "processors": processors,
                "evidence_id": str(job.evidence_id) if job.evidence_id else None,
                "case_id": evidence.case_id if evidence else None,
                "progress": None,
                "error": job.error,
            }
        finally:
            db.close()
