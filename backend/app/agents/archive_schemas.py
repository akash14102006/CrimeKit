"""
Pydantic contracts and schemas for CrimeKit Phase 10:
Tamper-Evident Case Sealing & Offline Forensic Archive.

Defines:
- CaseSeal: Cryptographic sealing certificate linking case metadata, roots, and verification status.
- MerkleSubtreeRoots: Individual sub-roots (evidence, findings, timeline, testimony, contradictions, review, report, provenance).
- CaseManifest: Comprehensive deterministic JSON manifest representing immutable case state snapshot.
- ArchiveValidationReport: Pre-seal checklist checking evidence hashes, reports, contradictions, and custody.
- CaseArchiveSummary: Overview returned by archive API endpoints.
- ArchiveVersionDiff: Comparison summary between archive version N and version N+1.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


class MerkleSubtreeRoots(BaseModel):
    evidence_root: str = Field(..., description="Root SHA-256 computed across ordered evidence items")
    findings_root: str = Field(..., description="Root SHA-256 computed across specialist findings")
    timeline_root: str = Field(..., description="Root SHA-256 computed across chronology items")
    testimony_root: str = Field(..., description="Root SHA-256 computed across extracted claims")
    contradiction_root: str = Field(..., description="Root SHA-256 computed across contradiction matrix items")
    review_root: str = Field(..., description="Root SHA-256 computed across investigator review decisions")
    report_root: str = Field(..., description="Root SHA-256 computed from generated report document")
    provenance_root: str = Field(..., description="Root SHA-256 computed across forensic provenance chain")


class CaseSeal(BaseModel):
    seal_id: str = Field(default_factory=lambda: f"SEAL-{uuid.uuid4().hex[:8].upper()}")
    case_id: str
    case_title: str
    version: int = 1
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_by: str
    case_status: Literal["open", "under_investigation", "closed", "sealed", "archived"] = "sealed"
    case_root_hash: str = Field(..., description="Master Merkle-style SHA-256 root of all subtrees")
    manifest_hash: str = Field(..., description="Deterministic SHA-256 of the complete manifest.json")
    evidence_count: int = 0
    subroots: MerkleSubtreeRoots
    blockchain_tx_hash: Optional[str] = None
    verification_status: Literal["VERIFIED", "VERIFICATION_FAILED", "UNVERIFIED"] = "VERIFIED"
    disclaimer: str = (
        "TAMPER-EVIDENT FORENSIC SEAL NOTICE: This seal provides cryptographic integrity verification "
        "across case artifacts. It records an immutable state hash and does NOT independently establish legal admissibility."
    )


class CaseManifest(BaseModel):
    case_id: str
    version: int = 1
    created_at: str
    sealed_by: str
    case_title: str
    case_status: str
    subroots: MerkleSubtreeRoots
    case_root_hash: str
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    testimony: List[Dict[str, Any]] = Field(default_factory=list)
    contradictions: List[Dict[str, Any]] = Field(default_factory=list)
    review_history: List[Dict[str, Any]] = Field(default_factory=list)
    provenance: List[Dict[str, Any]] = Field(default_factory=list)
    reports: List[Dict[str, Any]] = Field(default_factory=list)


class PreSealValidationCheck(BaseModel):
    item: str
    status: Literal["passed", "warning", "failed"]
    detail: str


class ArchiveValidationReport(BaseModel):
    case_id: str
    ready_for_seal: bool
    checks: List[PreSealValidationCheck] = Field(default_factory=list)
    evidence_count: int
    unresolved_contradictions_count: int
    confirmed_contradictions_count: int
    report_available: bool
    chain_of_custody_intact: bool
    validation_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ArchiveVersionDiff(BaseModel):
    case_id: str
    base_version: int
    target_version: int
    base_root_hash: str
    target_root_hash: str
    added_evidence: List[str] = Field(default_factory=list)
    removed_evidence: List[str] = Field(default_factory=list)
    modified_evidence: List[str] = Field(default_factory=list)
    added_findings_count: int = 0
    added_contradictions_count: int = 0
    review_status_changes: List[Dict[str, Any]] = Field(default_factory=list)
    diff_summary: str


class OfflineVerificationSummary(BaseModel):
    case_id: str
    version: int
    case_root_hash: str
    computed_root_hash: str
    manifest_hash: str
    computed_manifest_hash: str
    integrity_status: Literal["VERIFIED", "TAMPER_DETECTED", "FAILED"]
    checked_files_count: int
    mismatched_files: List[str] = Field(default_factory=list)
    details: str
