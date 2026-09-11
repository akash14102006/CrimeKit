"""TSK forensic data schemas — typed structures for disk image analysis."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ImageFormat(str, Enum):
    RAW = "raw"
    RAW_SPLIT = "raw_split"
    EWF_E01 = "ewf_e01"
    EWF_EX01 = "ewf_ex01"
    AFF = "aff"
    VMDK = "vmdk"
    VHD = "vhd"
    QCOW = "qcow"
    UNKNOWN = "unknown"


class FilesystemType(str, Enum):
    NTFS = "ntfs"
    FAT12 = "fat12"
    FAT16 = "fat16"
    FAT32 = "fat32"
    EXFAT = "exfat"
    EXT2 = "ext2"
    EXT3 = "ext3"
    EXT4 = "ext4"
    HFS = "hfs"
    APFS = "apfs"
    ISO9660 = "iso9660"
    UFS = "ufs"
    YAFFS2 = "yaffs2"
    RAW = "raw"
    SWAP = "swap"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class AllocationState(str, Enum):
    ALLOCATED = "allocated"
    UNALLOCATED = "unallocated"
    ORPHAN = "orphan"
    UNKNOWN = "unknown"


class ObjectType(str, Enum):
    FILE = "file"
    DIRECTORY = "directory"
    LINK = "link"
    BLOCK = "block"
    CHARACTER = "character"
    FIFO = "fifo"
    SOCKET = "socket"
    UNKNOWN = "unknown"


class TSKProcessingStage(str, Enum):
    EVIDENCE_ACCEPTED = "evidence_accepted"
    SHA256_VERIFIED = "sha256_verified"
    IMAGE_CAPABILITY_DETECTED = "image_capability_detected"
    IMAGE_OPENED = "image_opened"
    VOLUME_SYSTEM_DETECTED = "volume_system_detected"
    PARTITION_DISCOVERY = "partition_discovery"
    FILESYSTEM_DETECTION = "filesystem_detection"
    FILESYSTEM_OPENED = "filesystem_opened"
    ROOT_DIRECTORY_DISCOVERY = "root_directory_discovery"
    DIRECTORY_TRAVERSAL = "directory_traversal"
    FILE_ENUMERATION = "file_enumeration"
    METADATA_EXTRACTION = "metadata_extraction"
    ALLOCATION_CLASSIFICATION = "allocation_classification"
    DELETED_ORPHAN_ANALYSIS = "deleted_orphan_analysis"
    FILESYSTEM_TEMPORAL_EXTRACTION = "filesystem_temporal_extraction"
    ARTIFACT_EXTRACTION = "artifact_extraction"
    ARTIFACT_NORMALIZATION = "artifact_normalization"
    TIMELINE_GENERATION = "timeline_generation"
    TEXT_ROUTING = "text_routing"
    ENTITY_EXTRACTION = "entity_extraction"
    ENTITY_RESOLUTION = "entity_resolution"
    RELATIONSHIP_DISCOVERY = "relationship_discovery"
    NEO4J_ENRICHMENT = "neo4j_enrichment"
    SEARCH_INDEXING = "search_indexing"
    PROCESSING_COMPLETE = "processing_complete"


@dataclass
class TSKImageInfo:
    image_path: str
    image_format: ImageFormat
    image_size: int
    sector_size: int = 512
    supports_evidence: bool = True
    error: Optional[str] = None


@dataclass
class TSKPartitionInfo:
    index: int
    start_offset: int
    length: int
    description: str
    flags: str = ""
    type_code: str = ""
    source_image: str = ""


@dataclass
class TSKVolumeInfo:
    vs_type: str
    partitions: List[TSKPartitionInfo] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class TSKFilesystemInfo:
    fs_type: FilesystemType
    offset: int
    block_size: int
    block_count: int = 0
    inode_count: int = 0
    root_inum: int = 0
    first_inum: int = 0
    last_inum: int = 0
    source_partition: Optional[int] = None
    error: Optional[str] = None


@dataclass
class TSKFileInfo:
    name: str
    path: str
    metadata_addr: int
    object_type: ObjectType
    allocation_state: AllocationState
    size: int
    uid: int = 0
    gid: int = 0
    mode: int = 0
    atime: Optional[datetime] = None
    mtime: Optional[datetime] = None
    ctime: Optional[datetime] = None
    crtime: Optional[datetime] = None
    nlink: int = 0
    fs_type: Optional[FilesystemType] = None
    partition_index: Optional[int] = None
    parent_path: str = ""
    is_deleted: bool = False
    content_accessible: bool = True


@dataclass
class TSKArtifact:
    artifact_id: str
    case_id: str
    evidence_id: str
    processor: str
    processor_version: str
    source_image: str
    partition_index: Optional[int]
    filesystem_type: Optional[FilesystemType]
    file_path: str
    file_name: str
    metadata_addr: int
    allocation_state: AllocationState
    object_type: ObjectType
    size: int
    timestamps: Dict[str, Optional[str]]
    content_hash: Optional[str] = None
    content_reference: Optional[str] = None
    confidence: float = 1.0
    provenance: str = "tsk_native"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class TSKTimelineEvent:
    event_id: str
    case_id: str
    evidence_id: str
    event_type: str
    timestamp: str
    timestamp_type: str
    file_path: str
    file_name: str
    metadata_addr: int
    source: str
    processor: str = "tsk"
    confidence: float = 1.0


@dataclass
class TSKProcessingConfig:
    max_files_per_partition: int = 100000
    max_content_read_bytes: int = 10 * 1024 * 1024
    read_deleted_files: bool = True
    read_unallocated: bool = False
    extract_content_types: List[str] = field(default_factory=lambda: [
        "txt", "csv", "xml", "json", "html", "htm", "log", "ini", "cfg", "conf",
        "doc", "docx", "pdf", "xls", "xlsx", "ppt", "pptx",
        "eml", "msg",
    ])
    timeout_seconds: int = 600
    chunk_size: int = 65536
    worker_id: Optional[str] = None
    emit_events: bool = True
    case_id: str = ""
    evidence_id: str = ""
