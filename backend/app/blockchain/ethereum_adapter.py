"""
Ethereum / Polygon adapter for CrimeKit blockchain anchoring.

Uses web3.py (lazily imported) to interact with the EvidenceAnchor contract.
Supports gas estimation, nonce management, retry logic, and idempotency.
"""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Any, Optional

from .adapter import (
    AnchorNotFoundError,
    AnchorProvider,
    AnchorProviderError,
    AnchorRecord,
    AnchorResult,
    VerificationResult,
)
from .config import get_blockchain_config
from .commitment import _abi_encode_bytes32, _abi_encode_string, _abi_encode_uint256

logger = logging.getLogger(__name__)

# Minimal ABI for the EvidenceAnchor contract — only the functions we call
_EVIDENCE_ANCHOR_ABI = [
    {
        "inputs": [
            {"name": "proofId", "type": "bytes32"},
            {"name": "caseCommitment", "type": "bytes32"},
            {"name": "evidenceCommitment", "type": "bytes32"},
            {"name": "merkleRoot", "type": "bytes32"},
            {"name": "anchorType", "type": "uint8"},
            {"name": "issuerId", "type": "bytes32"},
            {"name": "metadataHash", "type": "bytes32"},
        ],
        "name": "anchorProof",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "proofId", "type": "bytes32"},
        ],
        "name": "getAnchor",
        "outputs": [
            {
                "components": [
                    {"name": "proofId", "type": "bytes32"},
                    {"name": "caseCommitment", "type": "bytes32"},
                    {"name": "evidenceCommitment", "type": "bytes32"},
                    {"name": "merkleRoot", "type": "bytes32"},
                    {"name": "anchorType", "type": "uint8"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "issuerId", "type": "bytes32"},
                    {"name": "protocolVersion", "type": "uint256"},
                    {"name": "metadataHash", "type": "bytes32"},
                    {"name": "active", "type": "bool"},
                ],
                "name": "",
                "type": "tuple",
            },
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "proofId", "type": "bytes32"},
            {"name": "expectedRoot", "type": "bytes32"},
        ],
        "name": "verifyProof",
        "outputs": [
            {"name": "valid", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getAnchorCount",
        "outputs": [
            {"name": "", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

_ANCHOR_TYPE_MAP = {
    "evidence": 0,
    "batch": 1,
    "lineage": 2,
    "custody": 3,
    "verification": 4,
}


def _hash_identifier(value: str) -> bytes:
    """Hash an identifier into a 32-byte value for on-chain use."""
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return digest


class EthereumAnchorProvider(AnchorProvider):
    """
    Ethereum/Polygon anchor provider using web3.py.

    Connects to an EVM chain via RPC and submits anchorProof transactions
    to the EvidenceAnchor smart contract.
    """

    def __init__(
        self,
        rpc_url: str | None = None,
        contract_address: str | None = None,
        private_key: str | None = None,
        chain_id: int | None = None,
    ) -> None:
        cfg = get_blockchain_config()
        self._rpc_url = rpc_url or cfg.rpc_url
        self._contract_address = contract_address or cfg.contract_address
        self._private_key = private_key or cfg.private_key
        self._chain_id = chain_id or cfg.chain_id
        self._max_retries = cfg.max_retries
        self._explorer_url = cfg.explorer_url
        self._issuer_id = cfg.issuer_id

        self._web3: Any = None
        self._contract: Any = None
        self._account: Any = None
        self._connected = False

    # ── Connection ───────────────────────────────────────────────────────────

    def _ensure_connected(self) -> None:
        """Lazy-connect to the chain."""
        if self._connected and self._web3 is not None:
            return

        if not self._rpc_url:
            raise AnchorProviderError("BLOCKCHAIN_RPC_URL is not configured")
        if not self._contract_address:
            raise AnchorProviderError("BLOCKCHAIN_CONTRACT_ADDRESS is not configured")

        try:
            from web3 import Web3
            from eth_account import Account
        except ImportError as exc:
            raise AnchorProviderError(
                "web3.py is required for EthereumAnchorProvider. "
                "Install it with: pip install web3",
                cause=exc,
            ) from exc

        self._web3 = Web3(Web3.HTTPProvider(self._rpc_url))

        if not self._web3.is_connected():
            raise AnchorProviderError(
                f"Cannot connect to RPC at {self._rpc_url}"
            )

        self._contract = self._web3.eth.contract(
            address=Web3.to_checksum_address(self._contract_address),
            abi=_EVIDENCE_ANCHOR_ABI,
        )

        if self._private_key:
            self._account = Account.from_key(self._private_key)

        self._connected = True
        logger.info(
            "Connected to %s (chain %d) contract %s",
            self._rpc_url,
            self._chain_id,
            self._contract_address,
        )

    # ── Core Operations ─────────────────────────────────────────────────────

    def anchor_root(
        self,
        merkle_root: str,
        batch_id: str,
        case_id: str,
        evidence_id: str,
        anchor_type: str = "evidence",
    ) -> AnchorResult:
        self._ensure_connected()
        assert self._web3 is not None and self._contract is not None

        proof_id_bytes = _hash_identifier(f"{merkle_root}:{batch_id}")
        proof_id_hex = "0x" + proof_id_bytes.hex()
        case_commitment = "0x" + _hash_identifier(case_id).hex()
        evidence_commitment = "0x" + _hash_identifier(evidence_id).hex()
        merkle_root_padded = "0x" + merkle_root.zfill(64)[:64]
        issuer_id = "0x" + _hash_identifier(self._issuer_id or "crimekit-default").hex()
        metadata_hash = "0x" + hashlib.sha256(b"").hexdigest()

        anchor_type_int = _ANCHOR_TYPE_MAP.get(anchor_type, 0)

        # Idempotency check — if already anchored, return existing data
        try:
            existing = self._contract.functions.getAnchor(
                self._web3.to_bytes(hexstr=proof_id_hex)
            ).call()
            if existing[0] != b"\x00" * 32:
                return AnchorResult(
                    proof_id=proof_id_hex,
                    status="anchored",
                    chain_id=self._chain_id,
                    network=get_blockchain_config().network,
                    contract_address=self._contract_address,
                    merkle_root=merkle_root,
                )
        except Exception:
            pass  # Not yet anchored — proceed

        if not self._account:
            raise AnchorProviderError(
                "No private key configured — cannot send transactions. "
                "Set BLOCKCHAIN_PRIVATE_KEY for development."
            )

        nonce = self._web3.eth.get_transaction_count(self._account.address)
        gas_price = self._web3.eth.gas_price

        # Build transaction
        tx = self._contract.functions.anchorProof(
            self._web3.to_bytes(hexstr=proof_id_hex),
            self._web3.to_bytes(hexstr=case_commitment),
            self._web3.to_bytes(hexstr=evidence_commitment),
            self._web3.to_bytes(hexstr=merkle_root_padded),
            anchor_type_int,
            self._web3.to_bytes(hexstr=issuer_id),
            self._web3.to_bytes(hexstr=metadata_hash),
        ).build_transaction({
            "chainId": self._chain_id,
            "from": self._account.address,
            "nonce": nonce,
            "gasPrice": int(gas_price * 1.1),
            "gas": 500000,
        })

        signed_tx = self._web3.eth.account.sign_transaction(
            tx, private_key=self._private_key
        )

        last_error: str | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                tx_hash = self._web3.eth.send_raw_transaction(
                    signed_tx.raw_transaction
                )
                receipt = self._web3.eth.wait_for_transaction_receipt(
                    tx_hash, timeout=120
                )

                if receipt.status == 1:
                    explorer = None
                    if self._explorer_url:
                        explorer = f"{self._explorer_url}/tx/{tx_hash.hex()}"

                    return AnchorResult(
                        proof_id=proof_id_hex,
                        tx_hash=tx_hash.hex(),
                        block_number=receipt.blockNumber,
                        chain_id=self._chain_id,
                        network=get_blockchain_config().network,
                        contract_address=self._contract_address,
                        merkle_root=merkle_root,
                        status="anchored",
                        explorer_url=explorer,
                    )
                else:
                    last_error = f"Transaction reverted in block {receipt.blockNumber}"
                    logger.warning(
                        "Attempt %d/%d: tx reverted: %s",
                        attempt, self._max_retries, last_error,
                    )
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "Attempt %d/%d: %s", attempt, self._max_retries, last_error,
                )
                if attempt < self._max_retries:
                    time.sleep(min(2 ** attempt, 30))

        return AnchorResult(
            proof_id=proof_id_hex,
            status="failed",
            chain_id=self._chain_id,
            network=get_blockchain_config().network,
            contract_address=self._contract_address,
            merkle_root=merkle_root,
            error_message=last_error,
        )

    def get_anchor(self, proof_id: str) -> AnchorRecord:
        self._ensure_connected()
        assert self._web3 is not None and self._contract is not None

        proof_id_bytes = self._web3.to_bytes(hexstr=proof_id)
        try:
            result = self._contract.functions.getAnchor(proof_id_bytes).call()
        except Exception as exc:
            raise AnchorProviderError(
                f"Failed to read anchor for {proof_id}: {exc}", cause=exc
            ) from exc

        if result[0] == b"\x00" * 32:
            raise AnchorNotFoundError(proof_id)

        return AnchorRecord(
            proof_id="0x" + result[0].hex(),
            case_commitment="0x" + result[1].hex(),
            evidence_commitment="0x" + result[2].hex(),
            merkle_root="0x" + result[3].hex(),
            anchor_type=result[4],
            timestamp=result[5],
            issuer_id="0x" + result[6].hex(),
            protocol_version=result[7],
            metadata_hash="0x" + result[8].hex(),
            active=result[9],
        )

    def verify_anchor(
        self,
        proof_id: str,
        expected_root: str,
    ) -> VerificationResult:
        self._ensure_connected()
        assert self._web3 is not None and self._contract is not None

        proof_id_bytes = self._web3.to_bytes(hexstr=proof_id)
        expected_root_bytes = self._web3.to_bytes(
            hexstr="0x" + expected_root.zfill(64)[:64]
        )

        try:
            valid = self._contract.functions.verifyProof(
                proof_id_bytes, expected_root_bytes
            ).call()
        except Exception as exc:
            raise AnchorProviderError(
                f"Failed to verify anchor {proof_id}: {exc}", cause=exc
            ) from exc

        try:
            record = self.get_anchor(proof_id)
            return VerificationResult(
                proof_id=proof_id,
                exists=True,
                active=record.active,
                root_matches=valid,
                on_chain_root=record.merkle_root,
                anchor_type=record.anchor_type,
                timestamp=record.timestamp,
            )
        except AnchorNotFoundError:
            return VerificationResult(
                proof_id=proof_id,
                exists=False,
                active=False,
                root_matches=False,
            )
