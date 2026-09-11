"""Artifact normalization — maps TSK observations to CrimeKit unified schema."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..forensic_engine.schemas import EvidenceSchema
from .schemas import (
    AllocationState,
    FilesystemType,
    ObjectType,
    TSKArtifact,
    TSKFileInfo,
    TSKFilesystemInfo,
    TSKImageInfo,
    TSKPartitionInfo,
    TSKTimelineEvent,
)


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/") if path else "/"


def normalize_artifact(
    file_info: TSKFileInfo,
    case_id: str,
    evidence_id: str,
    image_info: TSKImageInfo,
    fs_info: Optional[TSKFilesystemInfo] = None,
    partition_info: Optional[TSKPartitionInfo] = None,
) -> TSKArtifact:
    return TSKArtifact(
        artifact_id=str(uuid.uuid4()),
        case_id=case_id,
        evidence_id=evidence_id,
        processor="tsk",
        processor_version="1.0.0",
        source_image=image_info.image_path,
        partition_index=partition_info.index if partition_info else (
            fs_info.source_partition if fs_info else None
        ),
        filesystem_type=fs_info.fs_type if fs_info else (
            file_info.fs_type or FilesystemType.UNKNOWN
        ),
        file_path=_normalize_path(file_info.path),
        file_name=file_info.name,
        metadata_addr=file_info.metadata_addr,
        allocation_state=file_info.allocation_state,
        object_type=file_info.object_type,
        size=file_info.size,
        timestamps={
            "atime": file_info.atime.isoformat() if file_info.atime else None,
            "mtime": file_info.mtime.isoformat() if file_info.mtime else None,
            "ctime": file_info.ctime.isoformat() if file_info.ctime else None,
            "crtime": file_info.crtime.isoformat() if file_info.crtime else None,
        },
        confidence=1.0,
        provenance="tsk_native",
    )


def normalize_timeline_events(
    files: List[TSKFileInfo],
    case_id: str,
    evidence_id: str,
    max_events: int = 50000,
) -> List[TSKTimelineEvent]:
    events: List[TSKTimelineEvent] = []
    timestamp_types = [
        ("atime", "FILE_ACCESSED"),
        ("mtime", "FILE_MODIFIED"),
        ("ctime", "FILE_CHANGED"),
        ("crtime", "FILE_CREATED"),
    ]
    for fi in files:
        if len(events) >= max_events:
            break
        for attr, event_type in timestamp_types:
            ts_val = getattr(fi, attr, None)
            if ts_val and ts_val.isoformat():
                events.append(TSKTimelineEvent(
                    event_id=str(uuid.uuid4()),
                    case_id=case_id,
                    evidence_id=evidence_id,
                    event_type=event_type,
                    timestamp=ts_val.isoformat(),
                    timestamp_type=attr,
                    file_path=_normalize_path(fi.path),
                    file_name=fi.name,
                    metadata_addr=fi.metadata_addr,
                    source="tsk_filesystem",
                    processor="tsk",
                    confidence=1.0,
                ))
    return events


def files_to_evidence_metadata(
    files: List[TSKFileInfo],
    artifacts: List[TSKArtifact],
) -> Dict[str, Any]:
    total = len(files)
    allocated = sum(1 for f in files if f.allocation_state == AllocationState.ALLOCATED)
    unallocated = sum(1 for f in files if f.allocation_state == AllocationState.UNALLOCATED)
    orphan = sum(1 for f in files if f.allocation_state == AllocationState.ORPHAN)
    deleted = sum(1 for f in files if f.is_deleted)
    dirs = sum(1 for f in files if f.object_type == ObjectType.DIRECTORY)
    regular = sum(1 for f in files if f.object_type == ObjectType.FILE)
    links = sum(1 for f in files if f.object_type == ObjectType.LINK)
    total_size = sum(f.size for f in files)
    fs_types = list({f.fs_type.value for f in files if f.fs_type and f.fs_type != FilesystemType.UNKNOWN})

    return {
        "tsk_summary": {
            "total_entries": total,
            "allocated": allocated,
            "unallocated": unallocated,
            "orphan": orphan,
            "deleted": deleted,
            "directories": dirs,
            "regular_files": regular,
            "links": links,
            "total_size_bytes": total_size,
            "filesystem_types": fs_types,
            "artifact_count": len(artifacts),
        }
    }
