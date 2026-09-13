"""
FastAPI router for the CrimeKit blockchain anchoring layer.

Provides endpoints for evidence anchoring, batch management, proof retrieval,
verification, provenance tracking, and protocol information.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import database, models
from ..auth import get_current_user, role_required
from . import batch as batch_service
from . import commitment as commitment_service
from .adapter import AnchorNotFoundError, AnchorProviderError
from .config import get_blockchain_config
from .ethereum_adapter import EthereumAnchorProvider
from .merkle import build_merkle_tree, generate_proof, verify_proof, MerkleProof
from .schemas import (
    AnchorBatchRequest,
    AnchorEvidenceRequest,
    AnchorResponse,
    AnchorStatusResponse,
    AnchorStatus,
    AnchorType,
    BatchStatus,
    BlockchainStatsResponse,
    MerkleBatchListResponse,
    MerkleBatchResponse,
    ProofBundle,
    ProofBundleResponse,
    ProvenanceGraphResponse,
    ProvenanceNode,
    ProtocolInfoResponse,
    VerifyProofBundleRequest,
    VerificationReport,
)
from .verification import verify_evidence, verify_from_proof_bundle

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/blockchain", tags=["blockchain"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_adapter() -> EthereumAnchorProvider | None:
    """Get the Ethereum adapter if blockchain is configured."""
    cfg = get_blockchain_config()
    if not cfg.enabled or not cfg.is_configured:
        return None
    return EthereumAnchorProvider()


# ── Evidence Anchoring ───────────────────────────────────────────────────────


@router.post("/anchor/evidence/{evidence_id}", response_model=AnchorResponse)
def anchor_evidence(
    evidence_id: str,
    body: Optional[AnchorEvidenceRequest] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(role_required(["admin", "investigator", "evidence_officer"])),
):
    """Anchor a single piece of evidence on the blockchain."""
    cfg = get_blockchain_config()
    if not cfg.enabled:
        raise HTTPException(status_code=503, detail="Blockchain anchoring is disabled")

    evidence = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    if body is None:
        body = AnchorEvidenceRequest(evidence_id=evidence_id, case_id=evidence.case_id)


    case_id = body.case_id
    case_commitment = hashlib.sha256(case_id.encode()).hexdigest() if case_id else "0" * 64
    evidence_commitment = hashlib.sha256(evidence.sha256.encode()).hexdigest() if evidence.sha256 else "0" * 64
    metadata_hash = commitment_service.compute_metadata_hash(body.metadata) if body.metadata else hashlib.sha256(b"").hexdigest()

    # Create the evidence commitment
    commitment_hash = commitment_service.create_evidence_commitment(
        evidence_sha256=evidence.sha256 or "",
        metadata=body.metadata,
        version=cfg.protocol_version,
    )

    commitment = models.EvidenceCommitment(
        evidence_id=evidence_id,
        commitment_hash=commitment_hash,
        evidence_sha256=evidence.sha256 or "",
        metadata_hash=metadata_hash,
        version=cfg.protocol_version,
        status="pending",
    )
    db.add(commitment)
    db.flush()

    # Add to batch queue
    batch_service.add_to_batch(
        db,
        commitment_id=commitment.id,
        commitment_hash=commitment_hash,
        evidence_id=evidence_id,
    )

    # If adapter is available, try immediate anchoring
    adapter = _get_adapter()
    if adapter:
        merkle_tree = build_merkle_tree([commitment_hash])
        try:
            result = adapter.anchor_root(
                merkle_root=merkle_tree.root,
                batch_id="",
                case_id=case_id,
                evidence_id=evidence_id,
                anchor_type=body.anchor_type.value,
            )

            anchor = models.BlockchainAnchor(
                proof_id=result.proof_id or commitment_hash[:64],
                case_id=case_id,
                evidence_id=evidence_id,
                anchor_type=body.anchor_type.value,
                merkle_root=merkle_tree.root,
                case_commitment=case_commitment,
                evidence_commitment=evidence_commitment,
                metadata_hash=metadata_hash,
                protocol_version=cfg.protocol_version,
                issuer_id=cfg.issuer_id,
                tx_hash=result.tx_hash,
                block_number=result.block_number,
                chain_id=cfg.chain_id,
                network=cfg.network,
                contract_address=cfg.contract_address or "",
                status=result.status,
                error_message=result.error_message,
                anchored_at=datetime.now(timezone.utc),
            )
            db.add(anchor)
            commitment.anchor_id = anchor.id
            commitment.status = result.status
            db.commit()

            return AnchorResponse(
                proof_id=anchor.proof_id,
                tx_hash=anchor.tx_hash,
                block_number=anchor.block_number,
                chain_id=cfg.chain_id,
                network=cfg.network,
                contract_address=cfg.contract_address or "",
                merkle_root=merkle_tree.root,
                anchor_type=body.anchor_type,
                status=AnchorStatus(result.status),
                anchored_at=anchor.anchored_at or datetime.now(timezone.utc),
                explorer_url=result.explorer_url,
            )
        except AnchorProviderError as exc:
            logger.warning("Immediate anchoring failed: %s", exc)

    # Fallback: batch will anchor later
    db.commit()
    return AnchorResponse(
        proof_id=commitment_hash[:64],
        tx_hash=None,
        block_number=None,
        chain_id=cfg.chain_id,
        network=cfg.network,
        contract_address=cfg.contract_address or "",
        merkle_root="",
        anchor_type=body.anchor_type,
        status=AnchorStatus.PENDING,
        anchored_at=datetime.now(timezone.utc),
    )


@router.post("/anchor/batch", response_model=AnchorResponse)
def anchor_batch_now(
    body: AnchorBatchRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(role_required(["admin"])),
):
    """Force-finalize and anchor the current pending batch immediately."""
    cfg = get_blockchain_config()
    if not cfg.enabled:
        raise HTTPException(status_code=503, detail="Blockchain anchoring is disabled")

    adapter = _get_adapter()
    pending = batch_service.get_pending_batch(db, limit=cfg.batch_size)
    if not pending:
        raise HTTPException(status_code=400, detail="No pending commitments to anchor")

    batch = batch_service.finalize_batch(db, pending)

    if not adapter:
        raise HTTPException(
            status_code=503,
            detail="Blockchain adapter not configured — batch finalized but not anchored",
        )

    result = batch_service.anchor_batch(db, batch, adapter)

    return AnchorResponse(
        proof_id=batch.merkle_root[:64],
        tx_hash=result.tx_hash,
        block_number=result.block_number,
        chain_id=cfg.chain_id,
        network=cfg.network,
        contract_address=cfg.contract_address or "",
        merkle_root=batch.merkle_root,
        anchor_type=AnchorType.BATCH,
        status=AnchorStatus(result.status),
        anchored_at=batch.anchored_at or datetime.now(timezone.utc),
        explorer_url=result.explorer_url,
    )


# ── Anchor Retrieval ─────────────────────────────────────────────────────────


@router.get("/anchor/{proof_id}", response_model=AnchorStatusResponse)
def get_anchor(
    proof_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Retrieve anchor details by proof ID."""
    anchor = db.query(models.BlockchainAnchor).filter(
        models.BlockchainAnchor.proof_id == proof_id
    ).first()
    if not anchor:
        raise HTTPException(status_code=404, detail="Anchor not found")

    return AnchorStatusResponse(
        proof_id=anchor.proof_id,
        status=AnchorStatus(anchor.status),
        tx_hash=anchor.tx_hash,
        block_number=anchor.block_number,
        chain_id=anchor.chain_id,
        network=anchor.network,
        contract_address=anchor.contract_address,
        merkle_root=anchor.merkle_root,
        anchor_type=AnchorType(anchor.anchor_type) if anchor.anchor_type else None,
        anchored_at=anchor.anchored_at,
        error_message=anchor.error_message,
        retry_count=anchor.retry_count,
    )


@router.get("/anchor/{proof_id}/status", response_model=AnchorStatusResponse)
def get_anchor_status(
    proof_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Check on-chain status of an anchor (alias for /anchor/{proof_id})."""
    return get_anchor(proof_id, db, current_user)


# ── Proof Bundle ─────────────────────────────────────────────────────────────


@router.get("/evidence/{evidence_id}/proof", response_model=ProofBundleResponse)
def get_proof_bundle(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get a self-contained proof bundle for independent verification."""
    evidence = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    commitment = db.query(models.EvidenceCommitment).filter(
        models.EvidenceCommitment.evidence_id == evidence_id,
    ).order_by(models.EvidenceCommitment.created_at.desc()).first()
    if not commitment:
        raise HTTPException(status_code=404, detail="No commitment found for this evidence")

    merkle_proof_list: list[str] = []
    merkle_root = ""
    leaf_index = 0

    if commitment.batch_id:
        batch = db.query(models.MerkleBatch).filter(
            models.MerkleBatch.id == commitment.batch_id
        ).first()
        if batch:
            merkle_root = batch.merkle_root
            leaves = (
                db.query(models.MerkleLeaf)
                .filter(models.MerkleLeaf.batch_id == batch.id)
                .order_by(models.MerkleLeaf.leaf_index.asc())
                .all()
            )
            leaf_hashes = [l.commitment_hash for l in leaves]
            tree = build_merkle_tree(leaf_hashes)

            my_leaf = next(
                (l for l in leaves if l.commitment_id == commitment.id),
                None,
            )
            if my_leaf and my_leaf.leaf_index < len(leaf_hashes):
                leaf_index = my_leaf.leaf_index
                proof = generate_proof(tree, leaf_index)
                merkle_proof_list = proof.siblings

    anchor = None
    if commitment.anchor_id:
        anchor = db.query(models.BlockchainAnchor).filter(
            models.BlockchainAnchor.id == commitment.anchor_id
        ).first()

    cfg = get_blockchain_config()

    return ProofBundleResponse(
        proof_id=commitment.commitment_hash[:64],
        evidence_id=evidence_id,
        case_id=evidence.case_id,
        evidence_sha256=evidence.sha256 or "",
        commitment_hash=commitment.commitment_hash,
        merkle_root=merkle_root or commitment.commitment_hash,
        merkle_proof=merkle_proof_list,
        merkle_leaf_index=leaf_index,
        tx_hash=anchor.tx_hash if anchor else None,
        block_number=anchor.block_number if anchor else None,
        chain_id=anchor.chain_id if anchor else cfg.chain_id,
        network=anchor.network if anchor else cfg.network,
        contract_address=anchor.contract_address if anchor else cfg.contract_address,
        anchor_timestamp=anchor.anchored_at.isoformat() if anchor and anchor.anchored_at else None,
        protocol_version=commitment.protocol_version,
        issuer_id=cfg.issuer_id,
    )


# ── Verification ─────────────────────────────────────────────────────────────


@router.post("/verify/evidence/{evidence_id}", response_model=VerificationReport)
def verify_evidence_endpoint(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Verify evidence anchoring integrity through the CrimeKit backend."""
    report = verify_evidence(db, evidence_id)

    req = models.VerificationRequest(
        evidence_id=evidence_id,
        requested_by=current_user.id if current_user else None,
        evidence_hash_match=report.evidence_hash_match,
        commitment_valid=report.commitment_valid,
        merkle_proof_valid=report.merkle_proof_valid,
        blockchain_confirmed=report.blockchain_confirmed,
        overall_result=report.overall_result,
        details=report.model_dump(),
    )
    db.add(req)
    db.commit()

    return report


@router.post("/verify/proof-bundle", response_model=VerificationReport)
def verify_proof_bundle_endpoint(
    body: VerifyProofBundleRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Verify evidence using a self-contained proof bundle (no backend required)."""
    report = verify_from_proof_bundle(body.proof_bundle)

    req = models.VerificationRequest(
        evidence_id=body.proof_bundle.evidence_id,
        requested_by=current_user.id if current_user else None,
        evidence_hash_match=report.evidence_hash_match,
        commitment_valid=report.commitment_valid,
        merkle_proof_valid=report.merkle_proof_valid,
        blockchain_confirmed=report.blockchain_confirmed,
        overall_result=report.overall_result,
        details=report.model_dump(),
    )
    db.add(req)
    db.commit()

    return report


# ── Merkle Batch Management ─────────────────────────────────────────────────


@router.get("/merkle/batches", response_model=MerkleBatchListResponse)
def list_merkle_batches(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List Merkle batches with pagination."""
    total = db.query(models.MerkleBatch).count()
    batches = (
        db.query(models.MerkleBatch)
        .order_by(models.MerkleBatch.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = [
        MerkleBatchResponse(
            id=b.id,
            merkle_root=b.merkle_root,
            leaf_count=b.leaf_count,
            tree_depth=b.tree_depth,
            batch_size=b.batch_size,
            status=BatchStatus(b.status),
            anchor_id=b.anchor_id,
            created_at=b.created_at,
            anchored_at=b.anchored_at,
        )
        for b in batches
    ]

    return MerkleBatchListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/merkle/batch/{batch_id}", response_model=MerkleBatchResponse)
def get_merkle_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get details of a specific Merkle batch."""
    batch = db.query(models.MerkleBatch).filter(models.MerkleBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return MerkleBatchResponse(
        id=batch.id,
        merkle_root=batch.merkle_root,
        leaf_count=batch.leaf_count,
        tree_depth=batch.tree_depth,
        batch_size=batch.batch_size,
        status=BatchStatus(batch.status),
        anchor_id=batch.anchor_id,
        created_at=batch.created_at,
        anchored_at=batch.anchored_at,
    )


# ── Provenance ───────────────────────────────────────────────────────────────


@router.get("/provenance/{evidence_id}", response_model=ProvenanceGraphResponse)
def get_provenance(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get the complete provenance graph for an evidence item."""
    from .provenance import build_lineage_graph

    graph = build_lineage_graph(db, evidence_id)

    nodes = [
        ProvenanceNode(
            artifact_id=n.artifact_id,
            parent_artifact_id=n.parent_artifact_id,
            artifact_hash=n.artifact_hash,
            operation_type=n.operation_type,
            tool_name=n.tool_name,
            tool_version=n.tool_version,
            processing_timestamp=n.processing_timestamp,
            status=n.status,
        )
        for n in graph.nodes
    ]

    return ProvenanceGraphResponse(
        evidence_id=evidence_id,
        root_artifact_id=graph.root_artifact_id,
        nodes=nodes,
        depth=graph.depth,
    )


# ── Stats & Protocol ────────────────────────────────────────────────────────


@router.get("/stats", response_model=BlockchainStatsResponse)
def get_blockchain_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get blockchain anchoring statistics."""
    cfg = get_blockchain_config()

    total_anchors = db.query(models.BlockchainAnchor).count()
    confirmed = db.query(models.BlockchainAnchor).filter(
        models.BlockchainAnchor.status.in_(["anchored", "confirmed"])
    ).count()
    pending = db.query(models.BlockchainAnchor).filter(
        models.BlockchainAnchor.status == "pending"
    ).count()
    failed = db.query(models.BlockchainAnchor).filter(
        models.BlockchainAnchor.status == "failed"
    ).count()
    total_batches = db.query(models.MerkleBatch).count()
    total_commitments = db.query(models.EvidenceCommitment).count()

    return BlockchainStatsResponse(
        total_anchors=total_anchors,
        confirmed_anchors=confirmed,
        pending_anchors=pending,
        failed_anchors=failed,
        total_batches=total_batches,
        total_commitments=total_commitments,
        network=cfg.network,
        chain_id=cfg.chain_id,
        contract_address=cfg.contract_address,
        protocol_version=cfg.protocol_version,
        blockchain_enabled=cfg.enabled,
    )


@router.get("/protocol", response_model=ProtocolInfoResponse)
def get_protocol_info():
    """Get protocol information for the blockchain anchoring layer."""
    cfg = get_blockchain_config()
    return ProtocolInfoResponse(
        protocol_name="CrimeKit Evidence Anchoring Protocol",
        protocol_version=f"CRIMEKIT-EIP-001 v{cfg.protocol_version}.0",
        specification="SHA-256 commitments anchored on EVM-compatible chains",
        hash_algorithm="SHA-256",
        anchor_types=["evidence", "batch", "lineage", "custody", "verification"],
        chain_id=cfg.chain_id,
        network=cfg.network,
        contract_address=cfg.contract_address,
    )
