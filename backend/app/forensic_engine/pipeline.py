import logging
import time
from typing import Dict, List, Optional, Type

from .schemas import EvidenceSchema, ForensicProcessorConfig, ProcessingResult, ProcessorPriority
from .base import BaseProcessor
from .processors import ALL_PROCESSORS
from .utils.metadata import classify_evidence, classify_forensic_image, extract_file_metadata
from .utils.hashing import compute_hashes, verify_integrity

try:
    from ..advanced_forensics import ALL_ADVANCED_PROCESSORS
except ImportError:
    ALL_ADVANCED_PROCESSORS = {}

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    """Orchestrates evidence processing through a chain of forensic processors."""

    def __init__(self, config: Optional[ForensicProcessorConfig] = None):
        self.config = config or ForensicProcessorConfig()
        self._processors: Dict[str, BaseProcessor] = {}
        self._register_all()

    def _register_all(self) -> None:
        all_procs = {**ALL_PROCESSORS, **ALL_ADVANCED_PROCESSORS}
        for name, cls in all_procs.items():
            if self.config.enabled_processors is None or name in self.config.enabled_processors:
                self._processors[name] = cls()

    def register_processor(self, processor: BaseProcessor) -> None:
        self._processors[processor.name] = processor

    def get_available_processors(self) -> List[str]:
        return list(self._processors.keys())

    def process(self, evidence: EvidenceSchema) -> ProcessingResult:
        start = time.time()
        result = ProcessingResult(evidence_id=evidence.evidence_id, success=False)

        try:
            self._run_integrity_check(evidence)
            self._run_metadata_extraction(evidence)
            self._run_applicable_processors(evidence)
            result.success = True
            result.schema = evidence
        except Exception as e:
            evidence.add_error("pipeline", str(e))
            result.errors.append(str(e))
            logger.error("Pipeline processing failed for %s: %s", evidence.evidence_id, e)

        result.duration_seconds = time.time() - start
        result.processors_run = list(evidence.processor_results.keys())
        result.errors = evidence.processing_errors[:]
        return result

    def _run_integrity_check(self, evidence: EvidenceSchema) -> None:
        if not verify_integrity(evidence.storage_path, evidence.sha256):
            evidence.add_error("integrity", "SHA-256 mismatch - evidence may be tampered")
            evidence.add_tag("integrity_warning")
        else:
            evidence.add_tag("integrity_verified")

    def _run_metadata_extraction(self, evidence: EvidenceSchema) -> None:
        file_meta = extract_file_metadata(evidence.storage_path)
        evidence.metadata.update(file_meta)
        forensic_image = classify_forensic_image(
            evidence.storage_path, evidence.filename, evidence.mime_type,
        )
        if forensic_image.get("is_forensic_image"):
            evidence.category = EvidenceCategory.FORENSIC_DISK_IMAGE
            evidence.metadata["forensic_image"] = forensic_image
            evidence.metadata["evidence_type"] = forensic_image["evidence_type"]
            evidence.metadata["image_format"] = forensic_image["image_format"]
            evidence.metadata["processor"] = forensic_image["processor"]
            evidence.metadata["capability"] = forensic_image["capability"]
            evidence.metadata["capability_reason"] = forensic_image["reason"]
        elif evidence.category.value == "unknown":
            evidence.category = classify_evidence(evidence.filename, evidence.mime_type)
        if evidence.category.value == "unknown":
            evidence.category = classify_evidence(evidence.filename, evidence.mime_type)

    def _run_applicable_processors(self, evidence: EvidenceSchema) -> None:
        sorted_processors = sorted(
            self._processors.values(),
            key=lambda p: p.priority.value,
        )
        for processor in sorted_processors:
            if processor.can_process(evidence):
                logger.info(
                    "Running processor '%s' on evidence %s",
                    processor.name, evidence.evidence_id,
                )
                try:
                    processor.process(evidence, self.config)
                    evidence.add_result(processor.name, {"status": "completed"})
                except Exception as e:
                    evidence.add_error(processor.name, str(e))
                    evidence.add_result(processor.name, {"status": "failed", "error": str(e)})
                    logger.error("Processor '%s' failed: %s", processor.name, e)

    def process_from_path(
        self, evidence_id: str, file_path: str, filename: str,
        sha256: str, size: int, mime_type: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> ProcessingResult:
        evidence = EvidenceSchema(
            evidence_id=evidence_id,
            case_id=case_id,
            storage_path=file_path,
            filename=filename,
            sha256=sha256,
            size=size,
            mime_type=mime_type,
        )
        return self.process(evidence)
