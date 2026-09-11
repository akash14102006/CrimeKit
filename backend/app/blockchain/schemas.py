"""
Pydantic request/response schemas for the blockchain anchoring layer.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class AnchorType(str, Enum):
    EVIDENCE = "evidence"
    BATCH = "batch"
    LINEAGE = "lineage"
    CUSTODY = "custody"
    VERIFICATION = "verification"


class AnchorStatus(str, Enum):
    PENDING = "pending"
    ANCHORED = "anchored"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REVOKED = "revoked"


class CommitmentStatus(str, Enum):
    PENDING = "pending"
    COMMITTED = "committed"
    ANCHORED = "anchored"
    FAILED = "failed"


class BatchStatus(str, Enum):
    COLLECTING = "collecting"
    FINALIZED = "finalized"
    ANCHORED = "anchored"
    FAILED = "failed"


# ── Request Schemas ──────────────────────────────────────────────────────────

class AnchorEvidenceRequest(BaseModel):
    case_id: str
    evidence_id: str
    anchor_type: AnchorType = AnchorType.EVIDENCE
    metadata: dict[str, Any] | None = None


class AnchorBatchRequest(BaseModel):
    force: bool = False


class ProofBundle(BaseModel):
    """Self-contained proof bundle for independent verification."""
    proof_id: str
    evidence_id: str
    case_id: str | None = None
    evidence_sha256: str
    commitment_hash: str
    merkle_root: str
    merkle_proof: list[str] = Field(default_factory=list)
    merkle_leaf_index: int = 0
    tx_hash: str | None = None
    block_number: int | None = None
    chain_id: int | None = None
    network: str | None = None
    contract_address: str | None = None
    anchor_timestamp: str | None = None
    protocol_version: int = 1
    issuer_id: str | None = None


class VerifyProofBundleRequest(BaseModel):
    proof_bundle: ProofBundle


# ── Response Schemas ─────────────────────────────────────────────────────────

class AnchorResponse(BaseModel):
    proof_id: str
    tx_hash: str | None = None
    block_number: int | None = None
    chain_id: int
    network: str
    contract_address: str
    merkle_root: str
    anchor_type: AnchorType
    status: AnchorStatus
    anchored_at: datetime
    explorer_url: str | None = None

    class Config:
        from_attributes = True


class AnchorStatusResponse(BaseModel):
    proof_id: str
    status: AnchorStatus
    tx_hash: str | None = None
    block_number: int | None = None
    chain_id: int | None = None
    network: str | None = None
    contract_address: str | None = None
    merkle_root: str | None = None
    anchor_type: AnchorType | None = None
    anchored_at: datetime | None = None
    error_message: str | None = None
    retry_count: int = 0

    class Config:
        from_attributes = True


class ProofBundleResponse(BaseModel):
    proof_id: str
    evidence_id: str
    case_id: str | None = None
    evidence_sha256: str
    commitment_hash: str
    merkle_root: str
    merkle_proof: list[str]
    merkle_leaf_index: int
    tx_hash: str | None = None
    block_number: int | None = None
    chain_id: int | None = None
    network: str | None = None
    contract_address: str | None = None
    anchor_timestamp: str | None = None
    protocol_version: int
    issuer_id: str | None = None

    class Config:
        from_attributes = True


class VerificationReport(BaseModel):
    evidence_id: str
    evidence_hash_match: bool
    commitment_valid: bool
    merkle_proof_valid: bool
    blockchain_confirmed: bool
    timestamp: str
    overall_result: bool
    details: dict[str, Any] = Field(default_factory=list)


class MerkleBatchResponse(BaseModel):
    id: str
    merkle_root: str
    leaf_count: int
    tree_depth: int
    batch_size: int
    status: BatchStatus
    anchor_id: str | None = None
    created_at: datetime
    anchored_at: datetime | None = None

    class Config:
        from_attributes = True


class MerkleBatchListResponse(BaseModel):
    items: list[MerkleBatchResponse]
    total: int
    limit: int
    offset: int


class ProvenanceNode(BaseModel):
    artifact_id: str
    parent_artifact_id: str | None = None
    artifact_hash: str
    operation_type: str
    tool_name: str | None = None
    tool_version: str | None = None
    processing_timestamp: str | None = None
    status: str


class ProvenanceGraphResponse(BaseModel):
    evidence_id: str
    root_artifact_id: str | None = None
    nodes: list[ProvenanceNode]
    depth: int


class BlockchainStatsResponse(BaseModel):
    total_anchors: int
    confirmed_anchors: int
    pending_anchors: int
    failed_anchors: int
    total_batches: int
    total_commitments: int
    network: str
    chain_id: int
    contract_address: str | None = None
    protocol_version: int
    blockchain_enabled: bool


class ProtocolInfoResponse(BaseModel):
    protocol_name: str
    protocol_version: str
    specification: str
    hash_algorithm: str
    anchor_types: list[str]
    chain_id: int
    network: str
    contract_address: str | None = None
