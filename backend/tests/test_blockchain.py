"""
Comprehensive tests for the CrimeKit blockchain anchoring layer.

Covers: Merkle trees, commitments, provenance tracking, verification,
adversarial/tamper detection, batch management, schema/model creation,
and end-to-end integration flows.
"""

import hashlib
import uuid
from datetime import datetime, timezone

import pytest

# ── Merkle Tree ──────────────────────────────────────────────────────────────

from backend.app.blockchain.merkle import MerkleTree, compute_root, _sha256


def _fake_hash(i: int) -> str:
    return hashlib.sha256(f"leaf-{i}".encode()).hexdigest()


# A. Merkle Tree Tests


def test_merkle_tree_empty():
    tree = MerkleTree([])
    assert tree.leaf_count == 0
    assert tree.root == _sha256(b"")
    assert tree.tree_depth == 0


def test_merkle_tree_single_leaf():
    leaf = _fake_hash(0)
    tree = MerkleTree([leaf])
    assert tree.leaf_count == 1
    assert tree.root == leaf
    assert tree.tree_depth == 0


def test_merkle_tree_two_leaves():
    leaves = [_fake_hash(0), _fake_hash(1)]
    tree = MerkleTree(leaves)
    assert tree.leaf_count == 2
    assert tree.tree_depth == 1
    # root is hash of pair
    expected = hashlib.sha256(
        bytes.fromhex(_fake_hash(0)) + bytes.fromhex(_fake_hash(1))
    ).hexdigest()
    assert tree.root == expected


def test_merkle_tree_power_of_two():
    leaves = [_fake_hash(i) for i in range(8)]
    tree = MerkleTree(leaves)
    assert tree.leaf_count == 8
    assert tree.tree_depth == 3
    # 8 leaves → 4 → 2 → 1 = depth 3
    assert len(tree._layers) == 4


def test_merkle_tree_odd_leaves():
    leaves = [_fake_hash(i) for i in range(5)]
    tree = MerkleTree(leaves)
    assert tree.leaf_count == 5
    # 5 padded to 8 → 4 → 2 → 1 = depth 3
    assert tree.tree_depth == 3
    assert len(tree.padded_leaves) == 8
    # last leaf duplicated
    assert tree.padded_leaves[5] == tree.padded_leaves[6] == tree.padded_leaves[7]


def test_merkle_tree_deterministic():
    leaves = [_fake_hash(i) for i in range(10)]
    t1 = MerkleTree(leaves)
    t2 = MerkleTree(leaves)
    assert t1.root == t2.root
    assert t1.root == compute_root(leaves)


def test_merkle_proof_generation():
    leaves = [_fake_hash(i) for i in range(8)]
    tree = MerkleTree(leaves)
    proof = tree.get_proof(3)
    assert isinstance(proof, list)
    assert len(proof) == tree.tree_depth


def test_merkle_proof_validation_valid():
    leaves = [_fake_hash(i) for i in range(8)]
    tree = MerkleTree(leaves)
    for idx in range(len(leaves)):
        proof = tree.get_proof(idx)
        assert MerkleTree.verify_proof(leaves[idx], proof, tree.root, idx)


def test_merkle_proof_validation_invalid_leaf():
    leaves = [_fake_hash(i) for i in range(4)]
    tree = MerkleTree(leaves)
    proof = tree.get_proof(0)
    wrong_leaf = _fake_hash(999)
    assert MerkleTree.verify_proof(wrong_leaf, proof, tree.root, 0) is False


def test_merkle_proof_validation_wrong_root():
    leaves = [_fake_hash(i) for i in range(4)]
    tree = MerkleTree(leaves)
    proof = tree.get_proof(1)
    wrong_root = _sha256(b"wrong")
    assert MerkleTree.verify_proof(leaves[1], proof, wrong_root, 1) is False


def test_merkle_proof_validation_tampered_sibling():
    leaves = [_fake_hash(i) for i in range(4)]
    tree = MerkleTree(leaves)
    proof = tree.get_proof(0)
    # tamper with one sibling in the proof
    tampered_proof = list(proof)
    tampered_proof[0] = _sha256(b"tampered")
    assert MerkleTree.verify_proof(leaves[0], tampered_proof, tree.root, 0) is False


def test_merkle_tree_large_batch():
    leaves = [_fake_hash(i) for i in range(128)]
    tree = MerkleTree(leaves)
    assert tree.leaf_count == 128
    # 128 = 2^7 → depth 7
    assert tree.tree_depth == 7
    # verify a proof from each leaf
    for idx in [0, 63, 127]:
        proof = tree.get_proof(idx)
        assert MerkleTree.verify_proof(leaves[idx], proof, tree.root, idx)


# B. Commitment Tests

from backend.app.blockchain.commitment import (
    compute_evidence_commitment,
    compute_artifact_commitment,
    compute_custody_commitment,
)


def test_evidence_commitment_deterministic():
    c1 = compute_evidence_commitment("ev-1", "abc123", {"key": "val"})
    c2 = compute_evidence_commitment("ev-1", "abc123", {"key": "val"})
    assert c1 == c2


def test_evidence_commitment_different_inputs():
    c1 = compute_evidence_commitment("ev-1", "abc123")
    c2 = compute_evidence_commitment("ev-2", "abc123")
    c3 = compute_evidence_commitment("ev-1", "def456")
    assert c1 != c2
    assert c1 != c3


def test_artifact_commitment_deterministic():
    c1 = compute_artifact_commitment("art-1", "hash1", operation_type="extract")
    c2 = compute_artifact_commitment("art-1", "hash1", operation_type="extract")
    assert c1 == c2


def test_custody_commitment_deterministic():
    c1 = compute_custody_commitment("ev-1", "transfer", "user-1", metadata={"loc": "lab"})
    c2 = compute_custody_commitment("ev-1", "transfer", "user-1", metadata={"loc": "lab"})
    assert c1 == c2


def test_commitment_includes_version():
    c_v1 = compute_evidence_commitment("ev-1", "abc", protocol_version=1)
    c_v2 = compute_evidence_commitment("ev-1", "abc", protocol_version=2)
    assert c_v1 != c_v2


# C. Provenance Tests

from backend.app.blockchain.provenance import ProvenanceTracker


def test_provenance_lineage_tracking():
    tracker = ProvenanceTracker()
    tracker.register("orig-1", "hash-orig", "upload")
    tracker.register("derived-1", "hash-derived", "ocr", parent_artifact_id="orig-1")
    lineage = tracker.get_lineage("derived-1")
    assert len(lineage) == 2
    assert lineage[0].artifact_id == "orig-1"
    assert lineage[1].artifact_id == "derived-1"


def test_provenance_derived_artifacts():
    tracker = ProvenanceTracker()
    tracker.register("root", "h0", "upload")
    tracker.register("a1", "h1", "ocr", parent_artifact_id="root")
    tracker.register("a2", "h2", "resize", parent_artifact_id="root")
    tracker.register("a3", "h3", "annotate", parent_artifact_id="a1")
    derived = tracker.get_derived_artifacts("root")
    derived_ids = {d.artifact_id for d in derived}
    assert derived_ids == {"a1", "a2", "a3"}


def test_provenance_graph_construction():
    tracker = ProvenanceTracker()
    tracker.register("root", "h0", "upload")
    tracker.register("child1", "h1", "process", parent_artifact_id="root")
    graph = tracker.build_graph("ev-1")
    assert graph["evidence_id"] == "ev-1"
    assert graph["root_artifact_id"] == "root"
    assert len(graph["nodes"]) == 2
    assert graph["depth"] == 1


# D. Verification Tests

from backend.app.blockchain.verification import (
    verify_evidence_integrity,
    verify_merkle_proof,
    verify_commitment,
    verify_full_report,
)


def test_verify_evidence_integrity_match():
    h = hashlib.sha256(b"data").hexdigest()
    assert verify_evidence_integrity(h, h) is True


def test_verify_evidence_integrity_mismatch():
    h1 = hashlib.sha256(b"data1").hexdigest()
    h2 = hashlib.sha256(b"data2").hexdigest()
    assert verify_evidence_integrity(h1, h2) is False


def test_verify_merkle_proof_valid():
    leaves = [_fake_hash(i) for i in range(8)]
    tree = MerkleTree(leaves)
    for idx in range(8):
        proof = tree.get_proof(idx)
        assert verify_merkle_proof(leaves[idx], proof, tree.root, idx) is True


def test_verify_merkle_proof_invalid():
    leaves = [_fake_hash(i) for i in range(4)]
    tree = MerkleTree(leaves)
    proof = tree.get_proof(0)
    assert verify_merkle_proof(_fake_hash(999), proof, tree.root, 0) is False


def test_verify_commitment_valid():
    c = compute_evidence_commitment("ev-1", "hash1")
    assert verify_commitment(c, c) is True


def test_verify_commitment_tampered_metadata():
    c_original = compute_evidence_commitment("ev-1", "hash1", metadata={"key": "val"})
    c_tampered = compute_evidence_commitment("ev-1", "hash1", metadata={"key": "CHANGED"})
    assert verify_commitment(c_original, c_tampered) is False


def test_verify_full_report_success():
    evidence_hashes = [_fake_hash(i) for i in range(4)]
    commitments = [compute_evidence_commitment(f"ev-{i}", evidence_hashes[i]) for i in range(4)]
    tree = MerkleTree(commitments)
    idx = 2
    proof = tree.get_proof(idx)
    report = verify_full_report(
        evidence_id="ev-2",
        evidence_sha256=evidence_hashes[idx],
        expected_evidence_hash=evidence_hashes[idx],
        commitment_hash=commitments[idx],
        expected_commitment=commitments[idx],
        merkle_proof=proof,
        merkle_root=tree.root,
        merkle_leaf_index=idx,
    )
    assert report["overall_result"] is True
    assert report["evidence_hash_match"] is True
    assert report["commitment_valid"] is True
    assert report["merkle_proof_valid"] is True


def test_verify_full_report_hash_mismatch():
    evidence_hashes = [_fake_hash(i) for i in range(4)]
    commitments = [compute_evidence_commitment(f"ev-{i}", evidence_hashes[i]) for i in range(4)]
    tree = MerkleTree(commitments)
    proof = tree.get_proof(0)
    report = verify_full_report(
        evidence_id="ev-0",
        evidence_sha256=_fake_hash(999),
        expected_evidence_hash=evidence_hashes[0],
        commitment_hash=commitments[0],
        expected_commitment=commitments[0],
        merkle_proof=proof,
        merkle_root=tree.root,
        merkle_leaf_index=0,
    )
    assert report["overall_result"] is False
    assert report["evidence_hash_match"] is False


def test_verify_full_report_merkle_fail():
    evidence_hashes = [_fake_hash(i) for i in range(4)]
    commitments = [compute_evidence_commitment(f"ev-{i}", evidence_hashes[i]) for i in range(4)]
    tree = MerkleTree(commitments)
    proof = tree.get_proof(0)
    # wrong root
    report = verify_full_report(
        evidence_id="ev-0",
        evidence_sha256=evidence_hashes[0],
        expected_evidence_hash=evidence_hashes[0],
        commitment_hash=commitments[0],
        expected_commitment=commitments[0],
        merkle_proof=proof,
        merkle_root=_sha256(b"wrong"),
        merkle_leaf_index=0,
    )
    assert report["overall_result"] is False
    assert report["merkle_proof_valid"] is False


# E. Adversarial Tests


def test_tamper_one_bit_detection():
    """Flipping one bit in an evidence hash must be detectable."""
    original = _fake_hash(0)
    # flip the last hex char's LSB
    last_char = original[-1]
    flipped = hex(int(last_char, 16) ^ 1)[2:]
    tampered = original[:-1] + flipped
    assert original != tampered
    # commitment changes
    c_orig = compute_evidence_commitment("ev-1", original)
    c_tampered = compute_evidence_commitment("ev-1", tampered)
    assert c_orig != c_tampered
    # merkle root changes
    r1 = compute_root([original])
    r2 = compute_root([tampered])
    assert r1 != r2


def test_tamper_metadata_detection():
    """Changing metadata must produce a different commitment."""
    c1 = compute_evidence_commitment("ev-1", "hash", metadata={"seq": 1})
    c2 = compute_evidence_commitment("ev-1", "hash", metadata={"seq": 2})
    assert c1 != c2


def test_tamper_merkle_proof_detection():
    """Modifying any element in a Merkle proof must cause verification failure."""
    leaves = [_fake_hash(i) for i in range(8)]
    tree = MerkleTree(leaves)
    proof = tree.get_proof(5)
    for i in range(len(proof)):
        tampered = list(proof)
        tampered[i] = _sha256(b"adversarial")
        assert MerkleTree.verify_proof(leaves[5], tampered, tree.root, 5) is False


def test_wrong_root_detection():
    leaves = [_fake_hash(i) for i in range(4)]
    tree = MerkleTree(leaves)
    proof = tree.get_proof(0)
    assert MerkleTree.verify_proof(leaves[0], proof, _sha256(b"wrong"), 0) is False


def test_duplicate_commitment_detection():
    """Two different evidence items must not produce the same commitment."""
    c1 = compute_evidence_commitment("ev-1", "hashA")
    c2 = compute_evidence_commitment("ev-2", "hashB")
    assert c1 != c2


def test_replay_detection():
    """Replaying the same commitment must succeed (no replay protection at this layer,
    but changing evidence_id must change the commitment)."""
    c_orig = compute_evidence_commitment("ev-1", "hash")
    c_replay = compute_evidence_commitment("ev-1", "hash")
    c_new = compute_evidence_commitment("ev-2", "hash")
    # same inputs → same commitment (deterministic)
    assert c_orig == c_replay
    # different evidence_id → different commitment
    assert c_orig != c_new


# F. Batch Tests

from backend.app.blockchain.batch import BatchManager


def test_batch_add_commitment():
    mgr = BatchManager(batch_size=10)
    rec = mgr.add_commitment("ev-1", "sha-1")
    assert rec["evidence_id"] == "ev-1"
    assert rec["commitment_hash"] is not None
    assert mgr.pending_count == 1


def test_batch_finalization():
    mgr = BatchManager(batch_size=4)
    for i in range(4):
        mgr.add_commitment(f"ev-{i}", f"sha-{i}")
    batch = mgr.finalize_batch()
    assert batch is not None
    assert batch["leaf_count"] == 4
    assert batch["merkle_root"] is not None
    assert batch["status"] == "finalized"
    assert mgr.pending_count == 0
    assert mgr.batch_count == 1


def test_batch_merkle_root_correct():
    mgr = BatchManager()
    hashes = []
    for i in range(5):
        mgr.add_commitment(f"ev-{i}", f"sha-{i}")
        hashes.append(
            compute_evidence_commitment(f"ev-{i}", f"sha-{i}")
        )
    batch = mgr.finalize_batch()
    tree = MerkleTree(hashes)
    assert batch["merkle_root"] == tree.root


def test_batch_deterministic_root():
    mgr1 = BatchManager()
    mgr2 = BatchManager()
    for i in range(6):
        mgr1.add_commitment(f"ev-{i}", f"sha-{i}")
        mgr2.add_commitment(f"ev-{i}", f"sha-{i}")
    b1 = mgr1.finalize_batch()
    b2 = mgr2.finalize_batch()
    assert b1["merkle_root"] == b2["merkle_root"]


# G. Schema/Model Tests

from backend.app.blockchain.models import (
    BlockchainAnchor,
    EvidenceCommitment,
    MerkleBatch,
)


def test_blockchain_anchor_model_creation():
    anchor = BlockchainAnchor(
        batch_id="batch-1",
        chain_id=80002,
        network="polygon-amoy",
        merkle_root="root123",
        status="pending",
        retry_count=0,
    )
    assert anchor.batch_id == "batch-1"
    assert anchor.chain_id == 80002
    assert anchor.status == "pending"
    assert anchor.retry_count == 0


def test_evidence_commitment_model_creation():
    ec = EvidenceCommitment(
        evidence_id="ev-1",
        commitment_hash="commit123",
        evidence_sha256="sha123",
        protocol_version=1,
        status="pending",
    )
    assert ec.evidence_id == "ev-1"
    assert ec.protocol_version == 1
    assert ec.status == "pending"


def test_merkle_batch_model_creation():
    batch = MerkleBatch(
        merkle_root="root456",
        leaf_count=8,
        tree_depth=3,
        batch_size=128,
        status="collecting",
    )
    assert batch.merkle_root == "root456"
    assert batch.status == "collecting"
    assert batch.leaf_count == 8


# H. Integration Tests


def test_anchor_evidence_flow():
    """End-to-end: commit → batch → anchor."""
    mgr = BatchManager(batch_size=16)
    evidence_data = []
    for i in range(16):
        ev_id = f"ev-{i}"
        sha = hashlib.sha256(f"data-{i}".encode()).hexdigest()
        rec = mgr.add_commitment(ev_id, sha)
        evidence_data.append((ev_id, sha, rec["commitment_hash"]))

    batch = mgr.finalize_batch()
    assert batch["status"] == "finalized"
    assert batch["leaf_count"] == 16

    # simulate anchoring
    anchor_id = f"anchor-{uuid.uuid4().hex[:8]}"
    mgr.mark_anchored(batch["id"], anchor_id)
    updated = mgr.get_batch(batch["id"])
    assert updated["status"] == "anchored"
    assert updated["anchor_id"] == anchor_id


def test_verify_after_anchor():
    """Verify evidence integrity after it has been anchored."""
    mgr = BatchManager()
    ev_id = "ev-integration"
    sha = hashlib.sha256(b"integration-data").hexdigest()
    mgr.add_commitment(ev_id, sha)
    batch = mgr.finalize_batch()

    proof_info = mgr.get_proof_for_evidence(ev_id)
    assert proof_info is not None

    commitment = compute_evidence_commitment(ev_id, sha)
    report = verify_full_report(
        evidence_id=ev_id,
        evidence_sha256=sha,
        expected_evidence_hash=sha,
        commitment_hash=commitment,
        expected_commitment=commitment,
        merkle_proof=proof_info["merkle_proof"],
        merkle_root=proof_info["merkle_root"],
        merkle_leaf_index=proof_info["merkle_leaf_index"],
    )
    assert report["overall_result"] is True


def test_verify_tampered_evidence():
    """Detect tampered evidence after anchoring."""
    mgr = BatchManager()
    ev_id = "ev-tamper"
    sha_original = hashlib.sha256(b"original-data").hexdigest()
    mgr.add_commitment(ev_id, sha_original)
    batch = mgr.finalize_batch()

    proof_info = mgr.get_proof_for_evidence(ev_id)
    commitment = compute_evidence_commitment(ev_id, sha_original)

    # simulate tampering: evidence file is replaced
    sha_tampered = hashlib.sha256(b"tampered-data").hexdigest()

    report = verify_full_report(
        evidence_id=ev_id,
        evidence_sha256=sha_tampered,
        expected_evidence_hash=sha_original,
        commitment_hash=commitment,
        expected_commitment=commitment,
        merkle_proof=proof_info["merkle_proof"],
        merkle_root=proof_info["merkle_root"],
        merkle_leaf_index=proof_info["merkle_leaf_index"],
    )
    assert report["overall_result"] is False
    assert report["evidence_hash_match"] is False
