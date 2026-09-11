"""
Commitment scheme for CrimeKit blockchain anchoring.

Provides deterministic, tamper-evident commitment hashes for evidence,
artifacts, and custody operations.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional


DEFAULT_PROTOCOL_VERSION = 1


def _canonical_json(data: Dict[str, Any]) -> bytes:
    """Produce a deterministic JSON byte representation."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _commitment_hash(prefix: str, payload: bytes, version: int) -> str:
    """Compute a commitment hash: SHA-256(prefix + version_byte + payload)."""
    version_byte = version.to_bytes(2, byteorder="big")
    return hashlib.sha256(prefix.encode("ascii") + version_byte + payload).hexdigest()


def compute_evidence_commitment(
    evidence_id: str,
    evidence_sha256: str,
    metadata: Optional[Dict[str, Any]] = None,
    protocol_version: int = DEFAULT_PROTOCOL_VERSION,
) -> str:
    """
    Deterministic commitment hash for evidence integrity.

    Same inputs always produce the same commitment.
    """
    payload = _canonical_json({
        "evidence_id": evidence_id,
        "evidence_sha256": evidence_sha256,
        "metadata": metadata or {},
    })
    return _commitment_hash("EVIDENCE", payload, protocol_version)


def compute_artifact_commitment(
    artifact_id: str,
    artifact_hash: str,
    parent_artifact_id: Optional[str] = None,
    operation_type: str = "",
    tool_name: Optional[str] = None,
    tool_version: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    protocol_version: int = DEFAULT_PROTOCOL_VERSION,
) -> str:
    """
    Deterministic commitment hash for a derived artifact.
    Links to parent artifact for provenance tracking.
    """
    payload = _canonical_json({
        "artifact_id": artifact_id,
        "artifact_hash": artifact_hash,
        "parent_artifact_id": parent_artifact_id,
        "operation_type": operation_type,
        "tool_name": tool_name,
        "tool_version": tool_version,
        "metadata": metadata or {},
    })
    return _commitment_hash("ARTIFACT", payload, protocol_version)


def compute_custody_commitment(
    evidence_id: str,
    action: str,
    actor_id: str,
    previous_custody_hash: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    protocol_version: int = DEFAULT_PROTOCOL_VERSION,
) -> str:
    """
    Deterministic commitment hash for chain-of-custody operations.
    Chains to the previous custody hash for tamper detection.
    """
    payload = _canonical_json({
        "evidence_id": evidence_id,
        "action": action,
        "actor_id": actor_id,
        "previous_custody_hash": previous_custody_hash,
        "metadata": metadata or {},
    })
    return _commitment_hash("CUSTODY", payload, protocol_version)
