"""
CrimeKit Blockchain Anchoring Layer

Provides deterministic evidence anchoring on EVM-compatible chains (Polygon, Ethereum).
Only hashes and commitments are stored on-chain — never PII.

Modules:
    config       – Pydantic settings from environment variables
    models       – SQLAlchemy models for anchors, commitments, batches
    merkle       – Standard Merkle tree (SHA-256, sorted-pair hashing)
    commitment   – Deterministic commitment generation
    provenance   – Forensic lineage / provenance graph tracker
    adapter      – Abstract anchor provider interface
    ethereum_adapter – Ethereum/Polygon adapter (web3.py)
    verification – Independent proof verification service
    batch        – Batch anchoring with Redis queue (in-memory fallback)
    routes       – FastAPI router
    schemas      – Pydantic request/response schemas
"""

from __future__ import annotations

from .config import BlockchainConfig, get_blockchain_config
from .models import (
    ArtifactCommitment,
    BlockchainAnchor,
    CustodyCommitment,
    EvidenceCommitment,
    MerkleBatch,
    MerkleLeaf,
    VerificationRequest,
)

__all__ = [
    "BlockchainConfig",
    "get_blockchain_config",
    "ArtifactCommitment",
    "BlockchainAnchor",
    "CustodyCommitment",
    "EvidenceCommitment",
    "MerkleBatch",
    "MerkleLeaf",
    "VerificationRequest",
]
