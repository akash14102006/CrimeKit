"""
SQLAlchemy models for the CrimeKit blockchain anchoring layer.

These models store the on-disk representation of Merkle batches,
commitments, anchors, and verification requests.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from ..database import Base


class BlockchainAnchor(Base):
    """Records an on-chain anchor transaction for a Merkle batch."""
    __tablename__ = "blockchain_anchors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String, ForeignKey("merkle_batches.id"), nullable=False, index=True)
    tx_hash = Column(String, nullable=True)
    block_number = Column(Integer, nullable=True)
    chain_id = Column(Integer, nullable=False)
    network = Column(String, nullable=False)
    contract_address = Column(String, nullable=True)
    merkle_root = Column(String, nullable=False)
    anchor_type = Column(String, nullable=False, default="evidence")
    status = Column(String, nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    anchored_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)

    # relationship
    batch = relationship("MerkleBatch", back_populates="anchors")


class EvidenceCommitment(Base):
    """A cryptographic commitment for a piece of evidence."""
    __tablename__ = "evidence_commitments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False, index=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=True)
    commitment_hash = Column(String, nullable=False, index=True)
    evidence_sha256 = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    protocol_version = Column(Integer, nullable=False, default=1)
    batch_id = Column(String, ForeignKey("merkle_batches.id"), nullable=True, index=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    anchored_at = Column(DateTime(timezone=True), nullable=True)


class MerkleBatch(Base):
    """A finalized Merkle batch containing multiple evidence commitments."""
    __tablename__ = "merkle_batches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    merkle_root = Column(String, nullable=False, index=True)
    leaf_count = Column(Integer, nullable=False, default=0)
    tree_depth = Column(Integer, nullable=False, default=0)
    batch_size = Column(Integer, nullable=False, default=128)
    status = Column(String, nullable=False, default="collecting")
    anchor_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    anchored_at = Column(DateTime(timezone=True), nullable=True)

    # relationships
    anchors = relationship("BlockchainAnchor", back_populates="batch")
    leaves = relationship("MerkleLeaf", back_populates="batch")
    commitments = relationship("EvidenceCommitment", back_populates=None)


class MerkleLeaf(Base):
    """Individual leaf in a Merkle batch tree."""
    __tablename__ = "merkle_leaves"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String, ForeignKey("merkle_batches.id"), nullable=False, index=True)
    leaf_index = Column(Integer, nullable=False)
    leaf_hash = Column(String, nullable=False)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=True)
    commitment_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    batch = relationship("MerkleBatch", back_populates="leaves")


class ArtifactCommitment(Base):
    """A commitment for a derived artifact (part of provenance tracking)."""
    __tablename__ = "artifact_commitments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artifact_id = Column(String, nullable=False, index=True)
    parent_artifact_id = Column(String, nullable=True)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=True, index=True)
    artifact_hash = Column(String, nullable=False)
    commitment_hash = Column(String, nullable=False, index=True)
    operation_type = Column(String, nullable=False)
    tool_name = Column(String, nullable=True)
    tool_version = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    protocol_version = Column(Integer, nullable=False, default=1)
    status = Column(String, nullable=False, default="committed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CustodyCommitment(Base):
    """A commitment for chain-of-custody operations."""
    __tablename__ = "custody_commitments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False, index=True)
    custody_entry_id = Column(String, ForeignKey("chain_of_custody.id"), nullable=True)
    commitment_hash = Column(String, nullable=False, index=True)
    previous_custody_hash = Column(String, nullable=True)
    action = Column(String, nullable=False)
    actor_id = Column(String, ForeignKey("users.id"), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    protocol_version = Column(Integer, nullable=False, default=1)
    status = Column(String, nullable=False, default="committed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VerificationRequest(Base):
    """Records a verification request and its result."""
    __tablename__ = "verification_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False, index=True)
    requested_by = Column(String, ForeignKey("users.id"), nullable=True)
    evidence_hash_match = Column(Boolean, nullable=True)
    commitment_valid = Column(Boolean, nullable=True)
    merkle_proof_valid = Column(Boolean, nullable=True)
    blockchain_confirmed = Column(Boolean, nullable=True)
    overall_result = Column(Boolean, nullable=True)
    details = Column(JSON, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())


class BlockchainProtocol(Base):
    """Registry of supported blockchain protocols and versions."""
    __tablename__ = "blockchain_protocols"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    protocol_name = Column(String, nullable=False, unique=True)
    protocol_version = Column(String, nullable=False)
    specification = Column(Text, nullable=True)
    hash_algorithm = Column(String, nullable=False, default="sha256")
    anchor_types = Column(JSON, nullable=True)
    chain_id = Column(Integer, nullable=True)
    network = Column(String, nullable=True)
    contract_address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
