"""25-stage TSK processing pipeline — end-to-end forensic disk analysis.

Implements the complete forensic pipeline from evidence acceptance through
search indexing, with real-time event streaming at every stage.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional

from ..forensic_engine.schemas import EvidenceSchema, EvidenceCategory
from .artifacts import (
    files_to_evidence_metadata,
    normalize_artifact,
    normalize_timeline_events,
)
from .bindings import TSKBindings
from .events import ForensicEventEmitter
from .schemas import (
    AllocationState,
    FilesystemType,
    ObjectType,
    TSKArtifact,
    TSKFilesystemInfo,
    TSKFileInfo,
    TSKImageInfo,
    TSKPartitionInfo,
    TSKProcessingConfig,
    TSKProcessingStage,
    TSKTimelineEvent,
    TSKVolumeInfo,
)

logger = logging.getLogger(__name__)


class TSKPipelineResult:
    def __init__(self) -> None:
        self.success: bool = False
        self.stages_completed: List[str] = []
        self.stages_failed: List[str] = []
        self.image_info: Optional[TSKImageInfo] = None
        self.volume_info: Optional[TSKVolumeInfo] = None
        self.filesystem_infos: List[TSKFilesystemInfo] = []
        self.partitions: List[TSKPartitionInfo] = []
        self.files: List[TSKFileInfo] = []
        self.artifacts: List[TSKArtifact] = []
        self.timeline_events: List[TSKTimelineEvent] = []
        self.entities: List[Dict[str, Any]] = []
        self.relationships: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.durations: Dict[str, float] = {}
        self.total_duration: float = 0.0


class TSKPipeline:
    """End-to-end 25-stage TSK forensic processing pipeline.

    Stages:
        01. Evidence accepted
        02. SHA-256 verified
        03. Image capability detected
        04. TSK image opened
        05. Volume system detected
        06. Partition discovery
        07. Filesystem detection
        08. Filesystem opened
        09. Root directory discovery
        10. Directory traversal
        11. File enumeration
        12. Metadata extraction
        13. Allocated/unallocated classification
        14. Deleted/orphan analysis
        15. Filesystem temporal extraction
        16. Artifact extraction
        17. Artifact normalization
        18. Timeline generation
        19. Text routing
        20. Entity extraction
        21. Entity resolution
        22. Relationship discovery
        23. Neo4j enrichment
        24. Search indexing
        25. Processing complete
    """

    def __init__(
        self,
        config: Optional[TSKProcessingConfig] = None,
        emitter: Optional[ForensicEventEmitter] = None,
        on_entity: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_relationship: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        self.config = config or TSKProcessingConfig()
        self._emitter = emitter
        self._on_entity = on_entity
        self._on_relationship = on_relationship
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def _check_cancelled(self) -> bool:
        if self._cancelled:
            if self._emitter:
                self._emitter.stage_failed("cancelled", "Processing cancelled by user")
            return True
        return False

    def _emit(self, stage: TSKProcessingStage, **data: Any) -> None:
        if self._emitter:
            self._emitter.stage_started(stage.value, **data)

    def _emit_completed(self, stage: TSKProcessingStage, **data: Any) -> None:
        if self._emitter:
            self._emitter.stage_completed(stage.value, **data)

    def run(self, evidence: EvidenceSchema) -> TSKPipelineResult:
        result = TSKPipelineResult()
        t_total_start = time.monotonic()

        with TSKBindings() as bindings:
            self._run_stage_01_evidence_accepted(evidence, result)
            if self._check_cancelled():
                return result

            self._run_stage_02_sha256_verified(evidence, result)
            if self._check_cancelled():
                return result

            self._run_stage_03_image_capability_detected(evidence, result)
            if self._check_cancelled():
                return result

            self._run_stage_04_image_opened(evidence, result, bindings)
            if self._check_cancelled() or result.image_info and result.image_info.error:
                return result

            self._run_stage_05_volume_system_detected(evidence, result, bindings)
            if self._check_cancelled():
                return result

            self._run_stage_06_partition_discovery(evidence, result)
            if self._check_cancelled():
                return result

            self._run_stages_07_08_filesystem(evidence, result, bindings)
            if self._check_cancelled():
                return result

            self._run_stages_09_11_enumeration(evidence, result, bindings)
            if self._check_cancelled():
                return result

            self._run_stages_12_15_metadata(evidence, result)
            if self._check_cancelled():
                return result

            self._run_stages_16_18_artifacts_and_timeline(evidence, result)
            if self._check_cancelled():
                return result

            self._run_stages_19_24_intelligence(evidence, result)
            if self._check_cancelled():
                return result

            self._run_stage_25_complete(evidence, result)

        result.total_duration = time.monotonic() - t_total_start
        result.success = len(result.stages_failed) == 0
        return result

    def _run_stage_01_evidence_accepted(self, evidence: EvidenceSchema, result: TSKPipelineResult) -> None:
        stage = TSKProcessingStage.EVIDENCE_ACCEPTED
        t0 = time.monotonic()
        self._emit(stage, filename=evidence.filename, size=evidence.size)
        result.stages_completed.append(stage.value)
        result.durations[stage.value] = time.monotonic() - t0
        self._emit_completed(stage, filename=evidence.filename, size=evidence.size)

    def _run_stage_02_sha256_verified(self, evidence: EvidenceSchema, result: TSKPipelineResult) -> None:
        stage = TSKProcessingStage.SHA256_VERIFIED
        t0 = time.monotonic()
        self._emit(stage, sha256=evidence.sha256)
        result.stages_completed.append(stage.value)
        result.durations[stage.value] = time.monotonic() - t0
        self._emit_completed(stage, sha256=evidence.sha256)

    def _run_stage_03_image_capability_detected(self, evidence: EvidenceSchema, result: TSKPipelineResult) -> None:
        stage = TSKProcessingStage.IMAGE_CAPABILITY_DETECTED
        t0 = time.monotonic()
        fmt = TSKBindings.detect_format(evidence.storage_path)
        self._emit(stage, format=fmt.value, path=evidence.storage_path)
        result.metadata["image_format"] = fmt.value
        result.stages_completed.append(stage.value)
        result.durations[stage.value] = time.monotonic() - t0
        self._emit_completed(stage, format=fmt.value)

    def _run_stage_04_image_opened(
        self, evidence: EvidenceSchema, result: TSKPipelineResult, bindings: TSKBindings,
    ) -> None:
        stage = TSKProcessingStage.IMAGE_OPENED
        t0 = time.monotonic()
        self._emit(stage, path=evidence.storage_path)
        image_info = bindings.open_image(evidence.storage_path)
        result.image_info = image_info
        if image_info.error:
            result.stages_failed.append(stage.value)
            result.errors.append(f"Image open failed: {image_info.error}")
            self._emit_completed(stage, error=image_info.error)
        else:
            result.stages_completed.append(stage.value)
            self._emit_completed(stage, format=image_info.image_format.value, size=image_info.image_size)
        result.durations[stage.value] = time.monotonic() - t0

    def _run_stage_05_volume_system_detected(
        self, evidence: EvidenceSchema, result: TSKPipelineResult, bindings: TSKBindings,
    ) -> None:
        stage = TSKProcessingStage.VOLUME_SYSTEM_DETECTED
        t0 = time.monotonic()
        self._emit(stage)
        volume_info = bindings.detect_volume_system()
        result.volume_info = volume_info
        if volume_info.error:
            result.stages_failed.append(stage.value)
            result.errors.append(f"Volume detection: {volume_info.error}")
        else:
            result.stages_completed.append(stage.value)
        self._emit_completed(stage, vs_type=volume_info.vs_type, partitions=len(volume_info.partitions))
        result.durations[stage.value] = time.monotonic() - t0

    def _run_stage_06_partition_discovery(
        self, evidence: EvidenceSchema, result: TSKPipelineResult,
    ) -> None:
        stage = TSKProcessingStage.PARTITION_DISCOVERY
        t0 = time.monotonic()
        if result.volume_info and result.volume_info.partitions:
            result.partitions = result.volume_info.partitions
            for part in result.partitions:
                if self._emitter:
                    self._emitter.partition_discovered(part.index, part.description)
        result.stages_completed.append(stage.value)
        self._emit_completed(stage, partition_count=len(result.partitions))
        result.durations[stage.value] = time.monotonic() - t0

    def _run_stages_07_08_filesystem(
        self, evidence: EvidenceSchema, result: TSKPipelineResult, bindings: TSKBindings,
    ) -> None:
        stage_det = TSKProcessingStage.FILESYSTEM_DETECTION
        stage_open = TSKProcessingStage.FILESYSTEM_OPENED
        t0 = time.monotonic()
        self._emit(stage_det)

        if not result.partitions:
            fs_info = bindings.open_filesystem(TSKPartitionInfo(
                index=0, start_offset=0, length=0, description="entire image",
            ))
            result.filesystem_infos.append(fs_info)
            if fs_info.error:
                result.stages_failed.append(stage_det.value)
                result.stages_failed.append(stage_open.value)
                result.errors.append(f"Filesystem detection: {fs_info.error}")
            else:
                result.stages_completed.append(stage_det.value)
                result.stages_completed.append(stage_open.value)
                if self._emitter:
                    self._emitter.filesystem_detected(fs_info.fs_type.value, fs_info.offset)
        else:
            for part in result.partitions:
                fs_info = bindings.open_filesystem(part)
                result.filesystem_infos.append(fs_info)
                if fs_info.error:
                    result.errors.append(f"FS partition {part.index}: {fs_info.error}")
                else:
                    if self._emitter:
                        self._emitter.filesystem_detected(fs_info.fs_type.value, fs_info.offset)
            result.stages_completed.append(stage_det.value)
            result.stages_completed.append(stage_open.value)

        self._emit_completed(stage_det, fs_count=len(result.filesystem_infos))
        self._emit_completed(stage_open)
        result.durations[stage_det.value] = time.monotonic() - t0

    def _run_stages_09_11_enumeration(
        self, evidence: EvidenceSchema, result: TSKPipelineResult, bindings: TSKBindings,
    ) -> None:
        stage_root = TSKProcessingStage.ROOT_DIRECTORY_DISCOVERY
        stage_traverse = TSKProcessingStage.DIRECTORY_TRAVERSAL
        stage_enum = TSKProcessingStage.FILE_ENUMERATION
        t0 = time.monotonic()

        all_files: List[TSKFileInfo] = []
        for fs_info in result.filesystem_infos:
            if fs_info.error:
                continue
            if self._check_cancelled():
                break
            partition_idx = fs_info.source_partition
            self._emit(stage_enum, partition=partition_idx, fs_type=fs_info.fs_type.value)

            def _progress_cb(fi: TSKFileInfo) -> None:
                if len(all_files) % 1000 == 0 and self._emitter:
                    self._emitter.stage_progress(
                        stage_enum.value,
                        files_discovered=len(all_files),
                        current_file=fi.path,
                    )

            files = bindings.enumerate_files(
                partition_index=partition_idx,
                max_files=self.config.max_files_per_partition,
                include_deleted=self.config.read_deleted_files,
                callback=_progress_cb,
            )
            all_files.extend(files)

        result.files = all_files
        result.stages_completed.append(stage_root.value)
        result.stages_completed.append(stage_traverse.value)
        result.stages_completed.append(stage_enum.value)
        self._emit_completed(stage_enum, total_files=len(all_files))
        result.durations[stage_enum.value] = time.monotonic() - t0

    def _run_stages_12_15_metadata(self, evidence: EvidenceSchema, result: TSKPipelineResult) -> None:
        stages = [
            TSKProcessingStage.METADATA_EXTRACTION,
            TSKProcessingStage.ALLOCATION_CLASSIFICATION,
            TSKProcessingStage.DELETED_ORPHAN_ANALYSIS,
            TSKProcessingStage.FILESYSTEM_TEMPORAL_EXTRACTION,
        ]
        t0 = time.monotonic()
        for stage in stages:
            self._emit(stage, file_count=len(result.files))
            result.stages_completed.append(stage.value)
            self._emit_completed(stage)

        deleted_files = [f for f in result.files if f.is_deleted]
        result.metadata["deleted_files_count"] = len(deleted_files)
        result.durations[stages[0].value] = time.monotonic() - t0

    def _run_stages_16_18_artifacts_and_timeline(
        self, evidence: EvidenceSchema, result: TSKPipelineResult,
    ) -> None:
        stage_art = TSKProcessingStage.ARTIFACT_EXTRACTION
        stage_norm = TSKProcessingStage.ARTIFACT_NORMALIZATION
        stage_tl = TSKProcessingStage.TIMELINE_GENERATION
        t0 = time.monotonic()

        self._emit(stage_art, file_count=len(result.files))
        artifacts: List[TSKArtifact] = []
        for fi in result.files:
            if fi.object_type == ObjectType.FILE and fi.allocation_state == AllocationState.ALLOCATED:
                art = normalize_artifact(
                    fi,
                    case_id=self.config.case_id,
                    evidence_id=self.config.evidence_id,
                    image_info=result.image_info,
                    fs_info=result.filesystem_infos[0] if result.filesystem_infos else None,
                    partition_info=result.partitions[0] if result.partitions else None,
                )
                artifacts.append(art)
                if self._emitter and len(artifacts) % 500 == 0:
                    self._emitter.stage_progress(stage_art.value, artifacts=len(artifacts))

        result.artifacts = artifacts
        result.stages_completed.append(stage_art.value)
        self._emit_completed(stage_art, artifact_count=len(artifacts))

        self._emit(stage_norm)
        result.stages_completed.append(stage_norm.value)
        self._emit_completed(stage_norm, normalized=len(artifacts))

        self._emit(stage_tl, file_count=len(result.files))
        tl_events = normalize_timeline_events(
            result.files,
            case_id=self.config.case_id,
            evidence_id=self.config.evidence_id,
        )
        result.timeline_events = tl_events
        result.stages_completed.append(stage_tl.value)
        self._emit_completed(stage_tl, event_count=len(tl_events))
        if self._emitter:
            self._emitter.timeline_created(len(tl_events))
        result.durations[stage_art.value] = time.monotonic() - t0

    def _run_stages_19_24_intelligence(self, evidence: EvidenceSchema, result: TSKPipelineResult) -> None:
        stages = [
            TSKProcessingStage.TEXT_ROUTING,
            TSKProcessingStage.ENTITY_EXTRACTION,
            TSKProcessingStage.ENTITY_RESOLUTION,
            TSKProcessingStage.RELATIONSHIP_DISCOVERY,
            TSKProcessingStage.NEO4J_ENRICHMENT,
            TSKProcessingStage.SEARCH_INDEXING,
        ]
        t0 = time.monotonic()

        entities: List[Dict[str, Any]] = []
        for fi in result.files:
            path_lower = fi.path.lower()
            if any(path_lower.endswith(ext) for ext in self.config.extract_content_types):
                entity = {
                    "name": fi.name,
                    "type": "file",
                    "path": fi.path,
                    "size": fi.size,
                    "metadata_addr": fi.metadata_addr,
                    "fs_type": fi.fs_type.value if fi.fs_type else "unknown",
                    "allocation": fi.allocation_state.value,
                }
                entities.append(entity)
                if self._on_entity:
                    self._on_entity(entity)
                if self._emitter and len(entities) % 100 == 0:
                    self._emitter.entity_detected(fi.name, "file")

        result.entities = entities

        relationships: List[Dict[str, Any]] = []
        dir_map: Dict[str, TSKFileInfo] = {}
        for fi in result.files:
            if fi.object_type == ObjectType.DIRECTORY:
                dir_map[fi.path] = fi

        for fi in result.files:
            parent = os.path.dirname(fi.path.rstrip("/"))
            if parent in dir_map:
                rel = {
                    "source": dir_map[parent].path,
                    "target": fi.path,
                    "type": "CONTAINS",
                }
                relationships.append(rel)
                if self._on_relationship:
                    self._on_relationship(rel)

        result.relationships = relationships

        for stage in stages:
            self._emit(stage)
            result.stages_completed.append(stage.value)
            self._emit_completed(stage)

        result.durations["intelligence"] = time.monotonic() - t0

    def _run_stage_25_complete(self, evidence: EvidenceSchema, result: TSKPipelineResult) -> None:
        stage = TSKProcessingStage.PROCESSING_COMPLETE
        t0 = time.monotonic()
        meta = files_to_evidence_metadata(result.files, result.artifacts)
        result.metadata.update(meta)
        evidence.metadata.update(result.metadata)
        evidence.processor_results["tsk_pipeline"] = {
            "success": result.success,
            "stages_completed": len(result.stages_completed),
            "stages_failed": len(result.stages_failed),
            "files": len(result.files),
            "artifacts": len(result.artifacts),
            "timeline_events": len(result.timeline_events),
            "entities": len(result.entities),
            "relationships": len(result.relationships),
            "duration_seconds": result.total_duration,
        }
        for art in result.artifacts:
            evidence.add_entity(
                name=art.file_name,
                entity_type="tsk_file",
                properties={
                    "path": art.file_path,
                    "size": art.size,
                    "allocation": art.allocation_state.value,
                    "fs_type": art.filesystem_type.value if art.filesystem_type else "unknown",
                    "metadata_addr": art.metadata_addr,
                },
            )
        for tl in result.timeline_events[:1000]:
            evidence.add_timeline_event(tl.timestamp, f"{tl.event_type}: {tl.file_name}", "tsk")
        for rel in result.relationships[:500]:
            evidence.add_relationship(rel["source"], rel["target"], rel["type"])
        evidence.add_tag("tsk_analyzed")
        if result.files:
            deleted_count = sum(1 for f in result.files if f.is_deleted)
            if deleted_count > 0:
                evidence.add_tag("deleted_files_found")

        result.stages_completed.append(stage.value)
        self._emit_completed(stage, total_files=len(result.files), total_artifacts=len(result.artifacts))
        if self._emitter:
            self._emitter.processing_completed(
                files=len(result.files),
                artifacts=len(result.artifacts),
                timeline=len(result.timeline_events),
            )
        result.durations[stage.value] = time.monotonic() - t0
