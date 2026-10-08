"""
Pydantic contracts and schemas for CrimeKit Phase 8 Testimony Agent.

Defines:
- ClaimContract: Normalized model for factual assertions extracted from statements/depositions.
- AlibiVerificationContract: Structured result evaluating an asserted alibi against evidence.
- ContradictionContract: Formally structured discrepancy with explicit severity.
- TestimonyAnalysisRequest: Scoped request to extract and cross-check testimony.
- TestimonyAnalysisResult: Complete analysis bundle returned by Testimony Agent.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import uuid
import time


class ClaimContract(BaseModel):
    claim_id: str = Field(default_factory=lambda: f"CLM-{uuid.uuid4().hex[:6].upper()}")
    case_id: str = Field(..., description="Authoritative case identifier")
    testimony_id: Optional[str] = Field(None, description="Identifier of the source testimony or deposition")
    witness_id: Optional[str] = Field(None, description="Name or identifier of the testifying person")
    statement_text_ref: str = Field(..., description="Quoted sentence or excerpt from the transcript")
    subject: str = Field(..., description="Primary entity making the assertion or performing action")
    predicate: str = Field(..., description="Action, state, or assertion (e.g. was_present, made_call, met_with)")
    object: Optional[str] = Field(None, description="Object, co-present entity, or target of assertion")
    claimed_timestamp: Optional[str] = Field(None, description="ISO timestamp or approximate time stated")
    claimed_location: Optional[str] = Field(None, description="Stated location or landmark")
    entity_refs: List[str] = Field(default_factory=list, description="Extracted entity mentions")
    evidence_id: Optional[str] = Field(None, description="Source evidence artifact ID (e.g. EV-205)")
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    status: Literal["supported", "contradicted", "partially_supported", "unresolved", "needs_review"] = "needs_review"
    crosscheck_notes: Optional[str] = None


class ContradictionContract(BaseModel):
    contradiction_id: str = Field(default_factory=lambda: f"CONTRA-{uuid.uuid4().hex[:6].upper()}")
    case_id: str
    type: Literal["temporal", "geographic", "identity", "event", "sequence"] = "temporal"
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    claim_id: Optional[str] = None
    statement_excerpt: str
    evidence_fact: str
    evidence_refs: List[str] = Field(default_factory=list)
    difference_description: str
    status: Literal["needs_review", "verified_conflict", "resolved"] = "needs_review"


class AlibiVerificationContract(BaseModel):
    alibi_id: str = Field(default_factory=lambda: f"ALIBI-{uuid.uuid4().hex[:6].upper()}")
    case_id: str
    subject: str
    claimed_start: Optional[str] = None
    claimed_end: Optional[str] = None
    claimed_location: Optional[str] = None
    supporting_evidence_refs: List[str] = Field(default_factory=list)
    conflicting_evidence_refs: List[str] = Field(default_factory=list)
    unexplained_gaps: List[str] = Field(default_factory=list)
    assessment: str = Field(..., description="Objective evidentiary comparison (NO guilt/lie determination)")
    status: Literal["supported", "conflicted", "insufficient_records", "needs_review"] = "needs_review"
    confidence: float = 0.85


class TestimonyAnalysisRequest(BaseModel):
    __test__ = False
    case_id: str = Field(..., description="Authoritative case identifier")
    testimony_text: str = Field(..., min_length=10, description="Deposition, interview, or statement text")
    witness_name: Optional[str] = "Witness"
    evidence_id: Optional[str] = None
    focus_entities: List[str] = Field(default_factory=list)
    check_alibi: bool = False
    alibi_window: Optional[Dict[str, str]] = None


class TestimonyAnalysisResult(BaseModel):
    __test__ = False
    analysis_id: str = Field(default_factory=lambda: f"TESTIMONY-{uuid.uuid4().hex[:6].upper()}")
    case_id: str
    witness_name: str
    claims: List[ClaimContract] = Field(default_factory=list)
    contradictions: List[ContradictionContract] = Field(default_factory=list)
    alibi_analysis: Optional[AlibiVerificationContract] = None
    supporting_evidence_refs: List[str] = Field(default_factory=list)
    conflicting_evidence_refs: List[str] = Field(default_factory=list)
    summary: str
    review_status: Literal["needs_review", "reviewed", "verified"] = "needs_review"
    disclaimer: str = (
        "EVIDENTIARY COMPARISON NOTICE: CrimeKit extracts claims and compares them to digital records. "
        "CrimeKit DOES NOT determine witness credibility or make guilt determinations. All findings require human investigator review."
    )
