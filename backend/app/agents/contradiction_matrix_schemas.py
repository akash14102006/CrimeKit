"""
Pydantic contracts and schemas for CrimeKit Phase 9:
Interactive Contradiction Matrix & Evidence Verification Workspace.

Defines:
- ClaimEvidenceLink: Structured relation between a Claim and an Evidence record.
- ContradictionMatrixRow: Normalized matrix row combining claim, evidence, conflict, severity, and review.
- ContradictionReviewAction: Action payload submitted by an authorized investigator (Confirm, Dismiss, Unresolved).
- ReviewAuditTrailItem: Append-only ledger recording review decisions, notes, timestamps, and reviewers.
- EvidenceVerificationItem: Forensic verification details (SHA-256 match/mismatch, custody, chain-of-custody).
- EvidenceProvenanceNode: Graph/sequence node describing evidence intake -> extraction -> finding -> contradiction -> report.
- EvidenceVerificationPackageManifest: Cryptographic manifest listing real SHA-256 digests of exported review files.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone

from .testimony_schemas import ClaimContract, ContradictionContract


class ClaimEvidenceLink(BaseModel):
    link_id: str = Field(default_factory=lambda: f"LNK-{uuid.uuid4().hex[:6].upper()}")
    case_id: str = Field(..., description="Authoritative case identifier")
    claim_id: str = Field(..., description="Referenced ClaimContract ID")
    evidence_id: str = Field(..., description="Referenced Evidence record ID (e.g. EV-104)")
    relationship: Literal["supports", "contradicts", "partially_supports", "contextualizes", "unresolved"] = "contradicts"
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    source_agent: str = Field(default="testimony")
    finding_id: Optional[str] = None
    explanation: str = Field(..., description="Objective explanation of comparison")
    review_status: Literal["new", "needs_review", "confirmed", "dismissed", "unresolved"] = "needs_review"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReviewAuditTrailItem(BaseModel):
    audit_id: str = Field(default_factory=lambda: f"AUD-{uuid.uuid4().hex[:6].upper()}")
    case_id: str
    contradiction_id: str
    reviewer: str
    previous_status: str
    new_status: Literal["new", "needs_review", "confirmed", "dismissed", "unresolved"]
    note: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ContradictionReviewAction(BaseModel):
    case_id: str
    contradiction_id: str
    decision: Literal["confirmed", "dismissed", "unresolved"]
    note: Optional[str] = None


class ContradictionMatrixRow(BaseModel):
    claim: ClaimContract
    evidence_refs: List[str] = Field(default_factory=list)
    contradiction: Optional[ContradictionContract] = None
    links: List[ClaimEvidenceLink] = Field(default_factory=list)
    review_status: Literal["new", "needs_review", "confirmed", "dismissed", "unresolved"] = "needs_review"
    investigator_notes: List[str] = Field(default_factory=list)
    latest_decision_by: Optional[str] = None


class EvidenceVerificationItem(BaseModel):
    evidence_id: str
    filename: str
    stored_sha256: str
    computed_sha256: Optional[str] = None
    integrity_status: Literal["verified", "mismatch", "unavailable", "not_checked"] = "not_checked"
    chain_of_custody_available: bool = True
    custody_action_count: int = 0
    referenced_claim_ids: List[str] = Field(default_factory=list)
    referenced_finding_ids: List[str] = Field(default_factory=list)
    referenced_contradiction_ids: List[str] = Field(default_factory=list)
    review_status: Literal["needs_review", "verified", "flagged"] = "needs_review"


class EvidenceProvenanceNode(BaseModel):
    step: str  # "Evidence Intake", "Processing", "Extraction", "Agent Analysis", "Finding", "Contradiction", "Report"
    identifier: str
    description: str
    timestamp: Optional[str] = None
    agent: Optional[str] = None


class ContradictionMatrixResponse(BaseModel):
    case_id: str
    rows: List[ContradictionMatrixRow] = Field(default_factory=list)
    total_claims: int = 0
    total_contradictions: int = 0
    needs_review_count: int = 0
    confirmed_count: int = 0
    dismissed_count: int = 0
    unresolved_count: int = 0
    disclaimer: str = (
        "EVIDENTIARY COMPARISON NOTICE: CrimeKit organizes forensic discrepancies and calculates "
        "deterministic deltas. Does not determine witness veracity or make guilt conclusions. "
        "The investigator remains the decision-maker."
    )
