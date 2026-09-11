"""Standardized artifact models for all forensic processors.

Every processor outputs these normalized models for downstream integration
with AI Pipeline, Knowledge Graph, Timeline, and Investigation Workspace.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class ArtifactType(str, Enum):
    BROWSER_HISTORY = "browser_history"
    BROWSER_DOWNLOAD = "browser_download"
    BROWSER_BOOKMARK = "browser_bookmark"
    BROWSER_COOKIE = "browser_cookie"
    BROWSER_SESSION = "browser_session"
    BROWSER_CACHE = "browser_cache"
    BROWSER_SEARCH = "browser_search"
    BROWSER_AUTOFILL = "browser_autofill"
    BROWSER_EXTENSION = "browser_extension"
    BROWSER_PROFILE = "browser_profile"
    REGISTRY_KEY = "registry_key"
    PREFETCH = "prefetch"
    EVENT_LOG = "event_log"
    JUMPLIST = "jumplist"
    LNK_FILE = "lnk_file"
    SHELLBAG = "shellbag"
    SRUM = "srum"
    AMCACHE = "amcache"
    SHIMCACHE = "shimcache"
    USB_HISTORY = "usb_history"
    USERASSIST = "userassist"
    SCHEDULED_TASK = "scheduled_task"
    SERVICE_ENTRY = "service_entry"
    SMS = "sms"
    CALL_LOG = "call_log"
    CONTACT = "contact"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SIGNAL = "signal"
    IOS_PHOTO = "ios_photo"
    IOS_SAFARI = "ios_safari"
    IOS_KNOWLEDGEC = "ios_knowledgec"
    IOS_KEYCHAIN = "ios_keychain"
    EMAIL_HEADER = "email_header"
    EMAIL_BODY = "email_body"
    EMAIL_ATTACHMENT = "email_attachment"
    NETWORK_SESSION = "network_session"
    DNS_QUERY = "dns_query"
    HTTP_REQUEST = "http_request"
    TLS_HANDSHAKE = "tls_handshake"
    FILE_RECOVERY = "file_recovery"
    PARTITION_INFO = "partition_info"
    PROCESS = "process"
    NETWORK_CONNECTION = "network_connection"
    INJECTED_CODE = "injected_code"
    REGISTRY_HIVE = "registry_hive"
    CREDENTIAL = "credential"
    GENERIC = "generic"


class RiskLevel(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IOCType(str, Enum):
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"
    EMAIL = "email"
    FILE_PATH = "file_path"
    REGISTRY_KEY = "registry_key"
    MUTEX = "mutex"
    PROCESS_NAME = "process_name"
    USER_AGENT = "user_agent"


@dataclass
class Artifact:
    """Normalized forensic artifact extracted from evidence."""
    artifact_type: ArtifactType
    source: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    raw_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_type": self.artifact_type.value,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "tags": self.tags,
            "raw_path": self.raw_path,
        }


@dataclass
class IOC:
    """Indicator of Compromise."""
    ioc_type: IOCType
    value: str
    context: str = ""
    confidence: float = 0.8
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ioc_type": self.ioc_type.value,
            "value": self.value,
            "context": self.context,
            "confidence": self.confidence,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "tags": self.tags,
        }


@dataclass
class Finding:
    """Forensic finding requiring investigator attention."""
    title: str
    description: str
    risk_level: RiskLevel
    category: str
    evidence_refs: List[str] = field(default_factory=list)
    iocs: List[IOC] = field(default_factory=list)
    recommendation: str = ""
    mitre_attack: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "category": self.category,
            "evidence_refs": self.evidence_refs,
            "iocs": [i.to_dict() for i in self.iocs],
            "recommendation": self.recommendation,
            "mitre_attack": self.mitre_attack,
        }


@dataclass
class RiskIndicator:
    """Detected risk indicator."""
    indicator: str
    risk_level: RiskLevel
    source: str
    details: str = ""
    mitre_attack: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator": self.indicator,
            "risk_level": self.risk_level.value,
            "source": self.source,
            "details": self.details,
            "mitre_attack": self.mitre_attack,
        }


@dataclass
class EvidenceMetadata:
    """Standardized evidence metadata."""
    evidence_id: str
    filename: str
    sha256: str
    size: int
    mime_type: Optional[str]
    category: str
    source_system: str = ""
    acquisition_date: Optional[str] = None
    examiner: Optional[str] = None
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "filename": self.filename,
            "sha256": self.sha256,
            "size": self.size,
            "mime_type": self.mime_type,
            "category": self.category,
            "source_system": self.source_system,
            "acquisition_date": self.acquisition_date,
            "examiner": self.examiner,
            "chain_of_custody": self.chain_of_custody,
        }


@dataclass
class TimelineEvent:
    """Timeline event for chronological reconstruction."""
    timestamp: str
    event_type: str
    description: str
    source: str
    evidence_id: Optional[str] = None
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "description": self.description,
            "source": self.source,
            "evidence_id": self.evidence_id,
            "confidence": self.confidence,
            "tags": self.tags,
        }


@dataclass
class Entity:
    """Knowledge graph entity."""
    name: str
    entity_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.entity_type,
            "confidence": self.confidence,
            "source": self.source,
            **self.properties,
        }


@dataclass
class Relationship:
    """Knowledge graph relationship."""
    source: str
    target: str
    rel_type: str
    weight: int = 1
    properties: Dict[str, Any] = field(default_factory=dict)
    source_processor: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.rel_type,
            "weight": self.weight,
            **self.properties,
        }


# ---- Module-specific artifact models ----

@dataclass
class BrowserArtifact:
    """Browser forensics artifact."""
    browser: str
    artifact_type: str
    profile_name: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "browser": self.browser,
            "artifact_type": self.artifact_type,
            "profile_name": self.profile_name,
            "data": self.data,
            "timestamp": self.timestamp,
            "url": self.url,
            "title": self.title,
        }


@dataclass
class WindowsArtifact:
    """Windows forensics artifact."""
    artifact_type: str
    source_file: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None
    user_sid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_type": self.artifact_type,
            "source_file": self.source_file,
            "data": self.data,
            "timestamp": self.timestamp,
            "user_sid": self.user_sid,
        }


@dataclass
class MobileArtifact:
    """Mobile forensics artifact."""
    platform: str
    artifact_type: str
    source_db: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None
    contact: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "artifact_type": self.artifact_type,
            "source_db": self.source_db,
            "data": self.data,
            "timestamp": self.timestamp,
            "contact": self.contact,
        }


@dataclass
class EmailArtifact:
    """Email forensics artifact."""
    message_id: str
    subject: str
    sender: str
    recipients: List[str]
    timestamp: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    spf_result: Optional[str] = None
    dkim_result: Optional[str] = None
    dmarc_result: Optional[str] = None
    thread_id: Optional[str] = None
    hop_count: int = 0
    suspicious_indicators: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "subject": self.subject,
            "sender": self.sender,
            "recipients": self.recipients,
            "timestamp": self.timestamp,
            "headers": self.headers,
            "body": self.body,
            "attachments": self.attachments,
            "spf_result": self.spf_result,
            "dkim_result": self.dkim_result,
            "dmarc_result": self.dmarc_result,
            "thread_id": self.thread_id,
            "hop_count": self.hop_count,
            "suspicious_indicators": self.suspicious_indicators,
        }


@dataclass
class NetworkArtifact:
    """Network forensics artifact."""
    protocol: str
    source_ip: str
    dest_ip: str
    source_port: int
    dest_port: int
    timestamp: Optional[str] = None
    payload_summary: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol": self.protocol,
            "source_ip": self.source_ip,
            "dest_ip": self.dest_ip,
            "source_port": self.source_port,
            "dest_port": self.dest_port,
            "timestamp": self.timestamp,
            "payload_summary": self.payload_summary,
            "data": self.data,
        }


@dataclass
class DiskArtifact:
    """Disk image analysis artifact."""
    artifact_type: str
    partition: Optional[str] = None
    filesystem: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    recovered: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_type": self.artifact_type,
            "partition": self.partition,
            "filesystem": self.filesystem,
            "data": self.data,
            "recovered": self.recovered,
        }


@dataclass
class MemoryArtifact:
    """Memory forensics artifact."""
    artifact_type: str
    pid: Optional[int] = None
    process_name: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_type": self.artifact_type,
            "pid": self.pid,
            "process_name": self.process_name,
            "data": self.data,
            "address": self.address,
        }


@dataclass
class IntegrityResult:
    """Evidence integrity verification result."""
    verified: bool
    sha256_match: bool
    sha1_match: Optional[bool] = None
    md5_match: Optional[bool] = None
    perceptual_hash: Optional[str] = None
    yara_matches: List[str] = field(default_factory=list)
    clamav_result: Optional[str] = None
    entropy: Optional[float] = None
    extension_mismatch: bool = False
    header_mismatch: bool = False
    truncated: bool = False
    corrupted: bool = False
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verified": self.verified,
            "sha256_match": self.sha256_match,
            "sha1_match": self.sha1_match,
            "md5_match": self.md5_match,
            "perceptual_hash": self.perceptual_hash,
            "yara_matches": self.yara_matches,
            "clamav_result": self.clamav_result,
            "entropy": self.entropy,
            "extension_mismatch": self.extension_mismatch,
            "header_mismatch": self.header_mismatch,
            "truncated": self.truncated,
            "corrupted": self.corrupted,
            "details": self.details,
        }
