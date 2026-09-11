"""
Abstract anchor provider interface for CrimeKit blockchain layer.

Defines the contract that all blockchain adapters must implement.
Supports both synchronous and asynchronous usage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AnchorResult:
    """Result of an anchor operation."""
    proof_id: str
    tx_hash: str | None = None
    block_number: int | None = None
    chain_id: int | None = None
    network: str | None = None
    contract_address: str | None = None
    merkle_root: str | None = None
    status: str = "pending"
    error_message: str | None = None
    explorer_url: str | None = None


@dataclass
class AnchorRecord:
    """On-chain anchor record data."""
    proof_id: str
    case_commitment: str = ""
    evidence_commitment: str = ""
    merkle_root: str = ""
    anchor_type: int = 0
    timestamp: int = 0
    issuer_id: str = ""
    protocol_version: int = 1
    metadata_hash: str = ""
    active: bool = True


@dataclass
class VerificationResult:
    """Result of verifying an anchor on-chain."""
    proof_id: str
    exists: bool = False
    active: bool = False
    root_matches: bool = False
    on_chain_root: str = ""
    anchor_type: int = 0
    timestamp: int = 0
    block_number: int | None = None
    tx_hash: str | None = None


class AnchorProvider(ABC):
    """
    Abstract base class for blockchain anchor providers.

    All implementations must support:
    - anchor_root: submit a Merkle root to the blockchain
    - get_anchor: retrieve an anchor record by proof ID
    - verify_anchor: verify that an on-chain anchor matches an expected root
    """

    @abstractmethod
    def anchor_root(
        self,
        merkle_root: str,
        batch_id: str,
        case_id: str,
        evidence_id: str,
        anchor_type: str = "evidence",
    ) -> AnchorResult:
        """
        Anchor a Merkle root on the blockchain.

        Args:
            merkle_root: The hex-encoded Merkle root to anchor.
            batch_id: Internal batch identifier.
            case_id: Case identifier (hashed).
            evidence_id: Evidence identifier (hashed).
            anchor_type: Type of anchor (evidence, batch, lineage, custody).

        Returns:
            AnchorResult with transaction details.
        """
        ...

    @abstractmethod
    def get_anchor(self, proof_id: str) -> AnchorRecord:
        """
        Retrieve an anchor record from the blockchain.

        Args:
            proof_id: The unique proof identifier.

        Returns:
            AnchorRecord with on-chain data.

        Raises:
            AnchorNotFoundError: If the proof does not exist on-chain.
            AnchorProviderError: If the provider encounters an error.
        """
        ...

    @abstractmethod
    def verify_anchor(
        self,
        proof_id: str,
        expected_root: str,
    ) -> VerificationResult:
        """
        Verify that an on-chain anchor matches an expected Merkle root.

        Args:
            proof_id: The unique proof identifier.
            expected_root: The expected Merkle root to compare against.

        Returns:
            VerificationResult indicating whether the anchor is valid.
        """
        ...

    async def anchor_root_async(
        self,
        merkle_root: str,
        batch_id: str,
        case_id: str,
        evidence_id: str,
        anchor_type: str = "evidence",
    ) -> AnchorResult:
        """Async variant — default falls back to sync."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.anchor_root(merkle_root, batch_id, case_id, evidence_id, anchor_type),
        )

    async def get_anchor_async(self, proof_id: str) -> AnchorRecord:
        """Async variant — default falls back to sync."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.get_anchor(proof_id)
        )

    async def verify_anchor_async(
        self,
        proof_id: str,
        expected_root: str,
    ) -> VerificationResult:
        """Async variant — default falls back to sync."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.verify_anchor(proof_id, expected_root)
        )


class AnchorNotFoundError(Exception):
    """Raised when an anchor proof ID is not found on-chain."""

    def __init__(self, proof_id: str) -> None:
        self.proof_id = proof_id
        super().__init__(f"Anchor not found for proof_id: {proof_id}")


class AnchorProviderError(Exception):
    """Raised when the anchor provider encounters an operational error."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        self.cause = cause
        super().__init__(message)
