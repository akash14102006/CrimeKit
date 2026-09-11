from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import hashlib


class EvidenceCategory(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    PDF = "pdf"
    OFFICE = "office"
    EMAIL = "email"
    ARCHIVE = "archive"
    MOBILE_ARTIFACT = "mobile_artifact"
    DISK_IMAGE = "disk_image"
    FORENSIC_DISK_IMAGE = "forensic_disk_image"
    BROWSER_DATA = "browser_data"
    WINDOWS_ARTIFACT = "windows_artifact"
    NETWORK_CAPTURE = "network_capture"
    MEMORY_DUMP = "memory_dump"
    SYSTEM_ARTIFACT = "system_artifact"
    UNKNOWN = "unknown"


class ProcessorPriority(int, Enum):
    INTEGRITY = 0
    METADATA = 10
    TEXT_EXTRACTION = 20
    VISUAL = 30
    ARTIFACT_EXTRACTION = 35
    ANALYSIS = 40
    DEEP_ANALYSIS = 50


@dataclass
class EvidenceSchema:
    """Normalized evidence representation passed between processors."""
    evidence_id: str
    case_id: Optional[str]
    storage_path: str
    filename: str
    sha256: str
    size: int
    mime_type: Optional[str]
    category: EvidenceCategory = EvidenceCategory.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_text: Optional[str] = None
    thumbnails: Dict[str, bytes] = field(default_factory=dict)
    ocr_text: Optional[str] = None
    processing_errors: List[str] = field(default_factory=list)
    processor_results: Dict[str, Any] = field(default_factory=dict)
    timeline_events: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def add_result(self, processor_name: str, result: Dict[str, Any]) -> None:
        self.processor_results[processor_name] = result

    def add_error(self, processor_name: str, error: str) -> None:
        self.processing_errors.append(f"{processor_name}: {error}")

    def add_timeline_event(self, date: str, summary: str, source: str = "") -> None:
        self.timeline_events.append({"date": date, "summary": summary, "source": source})

    def add_entity(self, name: str, entity_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        self.entities.append({"name": name, "type": entity_type, **(properties or {})})

    def add_relationship(self, source: str, target: str, rel_type: str, weight: int = 1) -> None:
        self.relationships.append({"source": source, "target": target, "type": rel_type, "weight": weight})

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "case_id": self.case_id,
            "filename": self.filename,
            "sha256": self.sha256,
            "size": self.size,
            "mime_type": self.mime_type,
            "category": self.category.value,
            "metadata": self.metadata,
            "extracted_text": self.extracted_text,
            "ocr_text": self.ocr_text,
            "processing_errors": self.processing_errors,
            "processor_results": self.processor_results,
            "timeline_events": self.timeline_events,
            "entities": self.entities,
            "relationships": self.relationships,
            "tags": self.tags,
        }


@dataclass
class ForensicProcessorConfig:
    """Configuration for forensic processing pipeline."""
    enabled_processors: Optional[List[str]] = None
    ocr_language: str = "eng"
    thumbnail_size: tuple = (256, 256)
    max_pages_text: int = 10
    extract_media_metadata: bool = True
    generate_thumbnails: bool = True
    run_ocr: bool = True
    timeout_seconds: int = 300
    output_dir: Optional[str] = None


@dataclass
class ProcessingResult:
    """Result of processing a single evidence item through the pipeline."""
    evidence_id: str
    success: bool
    schema: Optional[EvidenceSchema] = None
    duration_seconds: float = 0.0
    processors_run: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
