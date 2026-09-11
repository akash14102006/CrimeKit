import type { ID, ISOString, Nullable } from "./common";

export type ImageFormat =
  | "raw"
  | "raw_split"
  | "ewf_e01"
  | "ewf_ex01"
  | "aff"
  | "vmdk"
  | "vhd"
  | "qcow"
  | "unknown";

export type FilesystemType =
  | "ntfs"
  | "fat12"
  | "fat16"
  | "fat32"
  | "exfat"
  | "ext2"
  | "ext3"
  | "ext4"
  | "hfs"
  | "apfs"
  | "iso9660"
  | "ufs"
  | "yaffs2"
  | "raw"
  | "swap"
  | "unsupported"
  | "unknown";

export type AllocationState =
  | "allocated"
  | "unallocated"
  | "orphan"
  | "unknown";

export type ObjectType =
  | "file"
  | "directory"
  | "link"
  | "block"
  | "character"
  | "fifo"
  | "socket"
  | "unknown";

export type TSKProcessingStage =
  | "evidence_accepted"
  | "sha256_verified"
  | "image_capability_detected"
  | "image_opened"
  | "volume_system_detected"
  | "partition_discovery"
  | "filesystem_detection"
  | "filesystem_opened"
  | "root_directory_discovery"
  | "directory_traversal"
  | "file_enumeration"
  | "metadata_extraction"
  | "allocation_classification"
  | "deleted_orphan_analysis"
  | "filesystem_temporal_extraction"
  | "artifact_extraction"
  | "artifact_normalization"
  | "timeline_generation"
  | "text_routing"
  | "entity_extraction"
  | "entity_resolution"
  | "relationship_discovery"
  | "neo4j_enrichment"
  | "search_indexing"
  | "processing_complete";

export interface TSKImageInfo {
  image_path: string;
  image_format: ImageFormat;
  image_size: number;
  sector_size: number;
  supports_evidence: boolean;
  error: Nullable<string>;
}

export interface TSKPartitionInfo {
  index: number;
  start_offset: number;
  length: number;
  description: string;
  flags: string;
  type_code: string;
  source_image: string;
}

export interface TSKVolumeInfo {
  vs_type: string;
  partitions: TSKPartitionInfo[];
  error: Nullable<string>;
}

export interface TSKFilesystemInfo {
  fs_type: FilesystemType;
  offset: number;
  block_size: number;
  block_count: number;
  inode_count: number;
  root_inum: number;
  first_inum: number;
  last_inum: number;
  source_partition: Nullable<number>;
  error: Nullable<string>;
}

export interface TSKFileInfo {
  name: string;
  path: string;
  metadata_addr: number;
  object_type: ObjectType;
  allocation_state: AllocationState;
  size: number;
  uid: number;
  gid: number;
  mode: number;
  atime: Nullable<ISOString>;
  mtime: Nullable<ISOString>;
  ctime: Nullable<ISOString>;
  crtime: Nullable<ISOString>;
  nlink: number;
  fs_type: Nullable<FilesystemType>;
  partition_index: Nullable<number>;
  parent_path: string;
  is_deleted: boolean;
  content_accessible: boolean;
  children?: TSKFileInfo[];
}

export interface TSKArtifact {
  artifact_id: ID;
  case_id: ID;
  evidence_id: ID;
  processor: string;
  processor_version: string;
  source_image: string;
  partition_index: Nullable<number>;
  filesystem_type: Nullable<FilesystemType>;
  file_path: string;
  file_name: string;
  metadata_addr: number;
  allocation_state: AllocationState;
  object_type: ObjectType;
  size: number;
  timestamps: Record<string, Nullable<string>>;
  content_hash: Nullable<string>;
  content_reference: Nullable<string>;
  confidence: number;
  provenance: string;
  created_at: string;
}

export interface TSKTimelineEvent {
  event_id: ID;
  case_id: ID;
  evidence_id: ID;
  event_type: string;
  timestamp: string;
  timestamp_type: string;
  file_path: string;
  file_name: string;
  metadata_addr: number;
  source: string;
  processor: string;
  confidence: number;
}

export interface TSKProcessingConfig {
  max_files_per_partition: number;
  max_content_read_bytes: number;
  read_deleted_files: boolean;
  read_unallocated: boolean;
  extract_content_types: string[];
  timeout_seconds: number;
  chunk_size: number;
  worker_id: Nullable<string>;
  emit_events: boolean;
  case_id: string;
  evidence_id: string;
}

export interface TSKCapabilities {
  tsk_version: string;
  pytsk_available: boolean;
  libewf_available: boolean;
  supported_image_formats: ImageFormat[];
  supported_filesystem_types: FilesystemType[];
  pipeline_stages: TSKProcessingStage[];
  max_files_per_partition: number;
  max_content_read_bytes: number;
  ewf?: { supported: boolean; reason: string };
}

export interface TSKProcessRequest {
  evidence_id: string;
  case_id: string;
  sync?: boolean;
}

export interface TSKEnqueueRequest {
  evidence_id: string;
  case_id: string;
  priority?: string;
}

export interface TSKPipelineResult {
  job_id: string;
  status: string;
  image_info: Nullable<TSKImageInfo>;
  volume_info: Nullable<TSKVolumeInfo>;
  filesystems: TSKFilesystemInfo[];
  files: TSKFileInfo[];
  artifacts: TSKArtifact[];
  timeline: TSKTimelineEvent[];
  metrics: TSKMetrics;
  errors: string[];
  started_at: string;
  completed_at: Nullable<string>;
  duration_ms: Nullable<number>;
}

export interface TSKMetrics {
  total_partitions: number;
  total_filesystems: number;
  total_files: number;
  total_directories: number;
  total_deleted: number;
  total_unallocated: number;
  total_orphan: number;
  total_size_bytes: number;
  artifacts_extracted: number;
  timeline_events: number;
  processing_time_ms: number;
}

export interface TSKJobStatus {
  job_id: string;
  status: string;
  current_stage: Nullable<TSKProcessingStage>;
  stages_completed: TSKProcessingStage[];
  stages_failed: TSKProcessingStage[];
  progress_percent: number;
  metrics: Nullable<TSKMetrics>;
  started_at: string;
  updated_at: string;
}
