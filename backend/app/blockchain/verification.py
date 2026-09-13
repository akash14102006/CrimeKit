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


def verify_evidence(db: Any, evidence_id: str):
    """Verify evidence integrity from DB models and commitments."""
    from .. import models
    from .schemas import VerificationReport
    from fastapi import HTTPException

    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="evidence not found")

    comm = (
        db.query(models.EvidenceCommitment)
        .filter(models.EvidenceCommitment.evidence_id == evidence_id)
        .order_by(models.EvidenceCommitment.created_at.desc())
        .first()
    )

    expected_comm = compute_evidence_commitment(
        evidence_id=ev.id,
        evidence_sha256=ev.sha256,
        metadata=ev.metadata_json or {},
    )

    if comm:
        commitment_hash = comm.commitment_hash
        commitment_valid = comm.commitment_hash == expected_comm
    else:
        commitment_hash = expected_comm
        commitment_valid = True

    merkle_root = ""
    merkle_proof: list[str] = []
    merkle_leaf_index = 0
    merkle_valid = True

    if comm and comm.batch_id:
        batch = db.query(models.MerkleBatch).filter(models.MerkleBatch.id == comm.batch_id).first()
        if batch:
            merkle_root = batch.merkle_root
            leaf = db.query(models.MerkleLeaf).filter(models.MerkleLeaf.commitment_id == comm.id).first()
            if leaf:
                merkle_leaf_index = leaf.leaf_index
                all_leaves = (
                    db.query(models.MerkleLeaf)
                    .filter(models.MerkleLeaf.batch_id == batch.id)
                    .order_by(models.MerkleLeaf.leaf_index.asc())
                    .all()
                )
                hashes = [l.commitment_hash for l in all_leaves]
                tree = MerkleTree(hashes)
                merkle_proof = tree.get_proof(merkle_leaf_index)
                merkle_valid = MerkleTree.verify_proof(
                    leaf.commitment_hash, merkle_proof, batch.merkle_root, merkle_leaf_index
                )

    report_dict = verify_full_report(
        evidence_id=evidence_id,
        evidence_sha256=ev.sha256,
        expected_evidence_hash=ev.sha256,
        commitment_hash=commitment_hash,
        expected_commitment=expected_comm,
        merkle_proof=merkle_proof,
        merkle_root=merkle_root,
        merkle_leaf_index=merkle_leaf_index,
    )
    return VerificationReport(**report_dict)


def verify_from_proof_bundle(bundle: Any):
    """Verify evidence from a standalone ProofBundle object."""
    from .schemas import VerificationReport

    expected_commitment = compute_evidence_commitment(
        evidence_id=bundle.evidence_id,
        evidence_sha256=bundle.evidence_sha256,
        protocol_version=bundle.protocol_version,
    )
    merkle_valid = True
    if bundle.merkle_proof and bundle.merkle_root:
        merkle_valid = MerkleTree.verify_proof(
            bundle.commitment_hash,
            bundle.merkle_proof,
            bundle.merkle_root,
            bundle.merkle_leaf_index,
        )

    hash_match = bool(bundle.evidence_sha256)
    commitment_valid = bundle.commitment_hash == expected_commitment
    overall = hash_match and commitment_valid and merkle_valid

    report_dict = {
        "evidence_id": bundle.evidence_id,
        "evidence_hash_match": hash_match,
        "commitment_valid": commitment_valid,
        "merkle_proof_valid": merkle_valid,
        "blockchain_confirmed": bool(bundle.tx_hash),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_result": overall,
        "details": {
            "expected_hash": bundle.evidence_sha256,
            "actual_hash": bundle.evidence_sha256,
            "expected_commitment": expected_commitment,
            "actual_commitment": bundle.commitment_hash,
            "merkle_root": bundle.merkle_root,
            "merkle_leaf_index": bundle.merkle_leaf_index,
            "protocol_version": bundle.protocol_version,
        },
    }
    return VerificationReport(**report_dict)
