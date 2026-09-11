"""
Verification service for CrimeKit blockchain anchoring.

Provides evidence integrity verification, Merkle proof validation,
commitment verification, and comprehensive verification reports.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .merkle import MerkleTree
from .commitment import (
    compute_evidence_commitment,
    compute_artifact_commitment,
    DEFAULT_PROTOCOL_VERSION,
)


def verify_evidence_integrity(
    evidence_sha256: str,
    expected_hash: str,
) -> bool:
    """Check that an evidence hash matches the expected value."""
    return evidence_sha256 == expected_hash


def verify_merkle_proof(
    leaf: str,
    proof: List[str],
    merkle_root: str,
    leaf_index: int,
) -> bool:
    """Verify a Merkle inclusion proof."""
    return MerkleTree.verify_proof(leaf, proof, merkle_root, leaf_index)


def verify_commitment(
    commitment_hash: str,
    expected_commitment: str,
) -> bool:
    """Check that a stored commitment matches the recomputed one."""
    return commitment_hash == expected_commitment


def verify_full_report(
    evidence_id: str,
    evidence_sha256: str,
    expected_evidence_hash: str,
    commitment_hash: str,
    expected_commitment: str,
    merkle_proof: List[str],
    merkle_root: str,
    merkle_leaf_index: int,
    protocol_version: int = DEFAULT_PROTOCOL_VERSION,
) -> Dict[str, Any]:
    """
    Generate a comprehensive verification report.

    Checks:
    1. Evidence hash integrity
    2. Commitment validity
    3. Merkle proof validity

    Returns a dict with individual results and an overall pass/fail.
    """
    hash_match = verify_evidence_integrity(evidence_sha256, expected_evidence_hash)
    commitment_valid = verify_commitment(commitment_hash, expected_commitment)
    merkle_valid = verify_merkle_proof(commitment_hash, merkle_proof, merkle_root, merkle_leaf_index)

    overall = hash_match and commitment_valid and merkle_valid

    return {
        "evidence_id": evidence_id,
        "evidence_hash_match": hash_match,
        "commitment_valid": commitment_valid,
        "merkle_proof_valid": merkle_valid,
        "blockchain_confirmed": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_result": overall,
        "details": {
            "expected_hash": expected_evidence_hash,
            "actual_hash": evidence_sha256,
            "expected_commitment": expected_commitment,
            "actual_commitment": commitment_hash,
            "merkle_root": merkle_root,
            "merkle_leaf_index": merkle_leaf_index,
            "protocol_version": protocol_version,
        },
    }
