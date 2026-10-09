"""
Pydantic contracts and schemas for CrimeKit Phase 7 Report Agent.

Enforces:
- ReportRequest: Bounded input specification with case isolation.
- ReportDocument: Structured forensic report document model.
- EvidenceIndexItem: Cryptographically verifiable evidence index row.
- HashLedgerItem: Source SHA-256 vs computed verification ledger.
- CustodySummaryItem: Chain of custody events summary.
- TimelineExhibitItem: Timestamp-preserved chronology exhibit row.
- GeospatialExhibitItem: GPS / cell tower location finding exhibit row.
- ContradictionExhibitItem: Preserved investigation contradiction.
- CertificateTemplate: Human-review certificate template (Section 65B style).
- ReportPackageManifest: SHA-256 hashed manifest for report export bundle.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


class ReportRequest(BaseModel):
    case_id: str = Field(..., description="Authoritative case identifier (must match session context)")
    title: str = Field(default="Forensic Investigation Report", min_length=3)
    objective: Optional[str] = Field(None, description="Investigative objective to focus on")
    finding_refs: List[str] = Field(default_factory=list, description="IDs of specific findings to include")
    evidence_refs: List[str] = Field(default_factory=list, description="Explicit evidence IDs to include")
    include_exhibits: bool = Field(default=True)
    include_hash_ledger: bool = Field(default=True)
    include_chain_of_custody: bool = Field(default=True)
    include_certificate_template: bool = Field(default=True)
    investigator_notes: Optional[str] = None


class EvidenceIndexItem(BaseModel):
    evidence_id: str
    filename: str
    sha256: str
    size_bytes: int = 0
    mime_type: Optional[str] = None
    uploaded_at: Optional[str] = None
    chain_of_custody_status: str = "verified"
    referenced_findings: List[str] = Field(default_factory=list)
    exhibit_number: str = "EX-01"


class HashLedgerItem(BaseModel):
    evidence_id: str
    filename: str
    stored_sha256: str
    computed_sha256: Optional[str] = None
    verification_status: Literal["verified", "mismatch", "unavailable", "not_checked"] = "not_checked"
    verified_at: Optional[str] = None
    notes: Optional[str] = None


class CustodySummaryItem(BaseModel):
    evidence_id: str
    action: str
    actor_id: Optional[str] = None
    timestamp: str
    notes: Optional[str] = None


class TimelineExhibitItem(BaseModel):
    event_id: str
    timestamp: str
    timezone: Optional[str] = "UTC"
    event_type: str
    description: str
    evidence_id: Optional[str] = None
    status: str = "supported"


class GeospatialExhibitItem(BaseModel):
    location_id: str
    latitude: float
    longitude: float
    timestamp: Optional[str] = None
    source_type: str = "gps"
    evidence_id: Optional[str] = None
    accuracy_meters: Optional[float] = None
    is_inferred: bool = False
    description: Optional[str] = None


class ContradictionExhibitItem(BaseModel):
    id: str
    type: str
    sources: List[str] = Field(default_factory=list)
    description: str
    status: str = "needs_review"


class CertificateTemplate(BaseModel):
    title: str = "ELECTRONIC EVIDENCE CERTIFICATE TEMPLATE"
    legal_framework_notice: str = (
        "TEMPLATE — REQUIRES AUTHORIZED HUMAN/LEGAL REVIEW. "
        "Does not constitute automated legal admissibility under Section 65B Indian Evidence Act / BSA or jurisdictional equivalent."
    )
    status: Literal["DRAFT", "PENDING_REVIEW", "EXECUTED"] = "DRAFT"
    case_id: str
    signatory_designation: str = "Digital Forensics Examiner / Lead Investigator"
    declaration_text: str
    signatory_name: str = "___________________________"
    signature_date: str = "___________________________"
    hash_affirmation: str


class ManifestFileEntry(BaseModel):
    path: str
    sha256: str
    size_bytes: int


class ReportPackageManifest(BaseModel):
    report_id: str
    case_id: str
    version: int = 1
    generated_at: str
    generated_by: str
    files: List[ManifestFileEntry] = Field(default_factory=list)
    evidence_items: List[Dict[str, str]] = Field(default_factory=list)
    overall_integrity_status: Literal["verified", "warning", "unverified"] = "verified"


class ReportDocument(BaseModel):
    report_id: str = Field(default_factory=lambda: f"RPT-{uuid.uuid4().hex[:8].upper()}")
    case_id: str
    title: str
    version: int = 1
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    generated_by: str = "CrimeKit Report Agent"
    objective: str
    methodology: List[str] = Field(default_factory=list)
    executive_summary: str
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_index: List[EvidenceIndexItem] = Field(default_factory=list)
    timeline_exhibits: List[TimelineExhibitItem] = Field(default_factory=list)
    geospatial_exhibits: List[GeospatialExhibitItem] = Field(default_factory=list)
    testimony_exhibits: List[Dict[str, Any]] = Field(default_factory=list, description="Witness claims and cross-checks")
    contradictions: List[ContradictionExhibitItem] = Field(default_factory=list)
    limitations_and_uncertainties: List[str] = Field(default_factory=list)
    hash_ledger: List[HashLedgerItem] = Field(default_factory=list)
    chain_of_custody: List[CustodySummaryItem] = Field(default_factory=list)
    certificate_template: Optional[CertificateTemplate] = None
    review_status: Literal["draft", "review_required", "reviewed", "finalized"] = "review_required"
    disclaimer: str = (
        "FORENSIC INTEGRITY NOTICE: CrimeKit organizes, correlates, and calculates cryptographic digests. "
        "CrimeKit DOES NOT determine guilt or automatic legal admissibility. All findings require independent human review."
    )
