"""
Batch management for CrimeKit blockchain anchoring.

Manages Merkle batch construction, finalization, and commitment tracking.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .merkle import MerkleTree, _sha256
from .commitment import compute_evidence_commitment, DEFAULT_PROTOCOL_VERSION


class BatchManager:
    """
    Manages Merkle batch collection and finalization.

    Commitments are collected into batches. When a batch is finalized,
    a Merkle tree is computed over all commitment hashes.
    """

    def __init__(self, batch_size: int = 128):
        self._batch_size = batch_size
        self._pending: List[Dict[str, Any]] = []
        self._batches: List[Dict[str, Any]] = []
        self._current_batch_id: Optional[str] = None

    @property
    def batch_size(self) -> int:
        return self._batch_size

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    @property
    def batch_count(self) -> int:
        return len(self._batches)

    @property
    def batches(self) -> List[Dict[str, Any]]:
        return list(self._batches)

    def add_commitment(
        self,
        evidence_id: str,
        evidence_sha256: str,
        metadata: Optional[Dict[str, Any]] = None,
        protocol_version: int = DEFAULT_PROTOCOL_VERSION,
    ) -> Dict[str, Any]:
        """
        Add an evidence commitment to the pending queue.

        Returns the commitment record.
        """
        commitment_hash = compute_evidence_commitment(
            evidence_id=evidence_id,
            evidence_sha256=evidence_sha256,
            metadata=metadata,
            protocol_version=protocol_version,
        )
        record = {
            "evidence_id": evidence_id,
            "evidence_sha256": evidence_sha256,
            "commitment_hash": commitment_hash,
            "metadata": metadata or {},
            "protocol_version": protocol_version,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self._pending.append(record)
        return record

    def get_pending(self) -> List[Dict[str, Any]]:
        return list(self._pending)

    def finalize_batch(self) -> Optional[Dict[str, Any]]:
        """
        Finalize the current pending commitments into a Merkle batch.

        Returns None if no pending commitments.
        Returns the batch record with Merkle root and tree info.
        """
        if not self._pending:
            return None

        batch_id = str(uuid.uuid4())
        commitments = list(self._pending)
        self._pending = []

        commitment_hashes = [c["commitment_hash"] for c in commitments]

        tree = MerkleTree(commitment_hashes)

        # Generate proofs for each commitment
        proofs = {}
        for i in range(len(commitment_hashes)):
            proofs[commitment_hashes[i]] = tree.get_proof(i)

        batch = {
            "id": batch_id,
            "merkle_root": tree.root,
            "leaf_count": len(commitment_hashes),
            "tree_depth": tree.tree_depth,
            "batch_size": self._batch_size,
            "commitments": commitments,
            "proofs": proofs,
            "status": "finalized",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "anchored_at": None,
            "anchor_id": None,
        }

        self._batches.append(batch)
        self._current_batch_id = batch_id
        return batch

    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        for b in self._batches:
            if b["id"] == batch_id:
                return b
        return None

    def get_proof_for_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Find the Merkle proof for a specific evidence in any finalized batch."""
        for batch in self._batches:
            for i, c in enumerate(batch["commitments"]):
                if c["evidence_id"] == evidence_id:
                    commitment_hash = c["commitment_hash"]
                    proof = batch["proofs"].get(commitment_hash, [])
                    return {
                        "batch_id": batch["id"],
                        "merkle_root": batch["merkle_root"],
                        "merkle_proof": proof,
                        "merkle_leaf_index": i,
                        "commitment_hash": commitment_hash,
                    }
        return None

    def mark_anchored(self, batch_id: str, anchor_id: str) -> bool:
        """Mark a batch as anchored on-chain."""
        for b in self._batches:
            if b["id"] == batch_id:
                b["status"] = "anchored"
                b["anchor_id"] = anchor_id
                b["anchored_at"] = datetime.now(timezone.utc).isoformat()
                return True
        return False
