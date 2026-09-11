"""Advanced Forensic Artifact Extraction Engine.

Enterprise-grade forensic analysis modules comparable to Autopsy, Magnet AXIOM, FTK.
Each module inherits from BaseProcessor and integrates into ProcessingPipeline.
"""
from .schemas import (
    Artifact, ArtifactType, IOC, IOCType, Finding, RiskIndicator, RiskLevel,
    EvidenceMetadata, TimelineEvent, Entity, Relationship,
    BrowserArtifact, WindowsArtifact, MobileArtifact,
    EmailArtifact, NetworkArtifact, DiskArtifact, MemoryArtifact, IntegrityResult,
)

from .browser import BrowserForensicsProcessor
from .windows import WindowsForensicsProcessor
from .mobile import MobileForensicsProcessor
from .email import EmailForensicsProcessor
from .network import NetworkForensicsProcessor
from .disk import DiskForensicsProcessor
from .memory import MemoryForensicsProcessor
from .integrity import IntegrityForensicsProcessor

ALL_ADVANCED_PROCESSORS = {
    "browser_forensics": BrowserForensicsProcessor,
    "windows_forensics": WindowsForensicsProcessor,
    "mobile_forensics": MobileForensicsProcessor,
    "email_forensics": EmailForensicsProcessor,
    "network_forensics": NetworkForensicsProcessor,
    "disk_forensics": DiskForensicsProcessor,
    "memory_forensics": MemoryForensicsProcessor,
    "integrity_forensics": IntegrityForensicsProcessor,
}

__all__ = [
    "Artifact", "ArtifactType", "IOC", "IOCType", "Finding", "RiskIndicator", "RiskLevel",
    "EvidenceMetadata", "TimelineEvent", "Entity", "Relationship",
    "BrowserArtifact", "WindowsArtifact", "MobileArtifact",
    "EmailArtifact", "NetworkArtifact", "DiskArtifact", "MemoryArtifact", "IntegrityResult",
    "BrowserForensicsProcessor", "WindowsForensicsProcessor", "MobileForensicsProcessor",
    "EmailForensicsProcessor", "NetworkForensicsProcessor", "DiskForensicsProcessor",
    "MemoryForensicsProcessor", "IntegrityForensicsProcessor",
    "ALL_ADVANCED_PROCESSORS",
]
