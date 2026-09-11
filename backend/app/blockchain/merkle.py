"""
Merkle tree implementation for CrimeKit blockchain anchoring.

Provides deterministic Merkle tree construction, root computation,
and inclusion proof generation/verification.
"""

from __future__ import annotations

import hashlib
from typing import List, Optional


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_pair(left: str, right: str) -> str:
    """Hash two hex-encoded hashes together deterministically (left-first)."""
    return _sha256(bytes.fromhex(left) + bytes.fromhex(right))


class MerkleTree:
    """Deterministic Merkle tree with padding for non-power-of-two leaf counts."""

    def __init__(self, leaves: Optional[List[str]] = None):
        self._leaves: List[str] = []
        self._padded_leaves: List[str] = []
        self._layers: List[List[str]] = []
        self._root: str = ""
        if leaves is not None:
            self.build(leaves)

    @property
    def root(self) -> str:
        return self._root

    @property
    def leaves(self) -> List[str]:
        return list(self._leaves)

    @property
    def leaf_count(self) -> int:
        return len(self._leaves)

    @property
    def tree_depth(self) -> int:
        return len(self._layers) - 1 if self._layers else 0

    @property
    def padded_leaves(self) -> List[str]:
        return list(self._padded_leaves)

    def build(self, leaves: List[str]) -> str:
        """Build the Merkle tree from a list of hex-encoded leaf hashes."""
        if not leaves:
            self._leaves = []
            self._padded_leaves = []
            self._layers = []
            self._root = _sha256(b"")
            return self._root

        self._leaves = list(leaves)

        # Pad to next power of two by duplicating the last leaf
        n = len(self._leaves)
        if n == 0:
            self._padded_leaves = []
            self._layers = []
            self._root = _sha256(b"")
            return self._root

        padded_count = 1
        while padded_count < n:
            padded_count *= 2

        self._padded_leaves = list(self._leaves)
        while len(self._padded_leaves) < padded_count:
            self._padded_leaves.append(self._padded_leaves[-1])

        # Build layers bottom-up
        self._layers = [list(self._padded_leaves)]
        current = self._padded_leaves
        while len(current) > 1:
            next_layer = []
            for i in range(0, len(current), 2):
                if i + 1 < len(current):
                    next_layer.append(_hash_pair(current[i], current[i + 1]))
                else:
                    next_layer.append(current[i])
            self._layers.append(next_layer)
            current = next_layer

        self._root = current[0] if current else _sha256(b"")
        return self._root

    def get_proof(self, leaf_index: int) -> List[str]:
        """
        Generate a Merkle inclusion proof for the leaf at the given index
        in the original (unpadded) leaf list.

        Returns a list of sibling hashes from bottom to top.
        """
        if leaf_index < 0 or leaf_index >= len(self._leaves):
            raise ValueError(f"leaf_index {leaf_index} out of range (0..{len(self._leaves) - 1})")

        if not self._layers:
            raise ValueError("Tree has not been built")

        # Map original index to padded index (same position)
        idx = leaf_index
        proof: List[str] = []

        for layer in self._layers[:-1]:
            if idx % 2 == 0:
                sibling = idx + 1
            else:
                sibling = idx - 1

            if sibling < len(layer):
                proof.append(layer[sibling])
            else:
                # Odd layer - no sibling at this level; the parent wraps up
                proof.append(layer[idx])

            idx = idx // 2

        return proof

    @staticmethod
    def verify_proof(leaf: str, proof: List[str], root: str, leaf_index: int) -> bool:
        """
        Verify a Merkle inclusion proof.

        Args:
            leaf: The hex-encoded hash of the leaf.
            proof: List of sibling hashes (from MerkleTree.get_proof).
            root: The expected Merkle root.
            leaf_index: The index of the leaf in the tree.

        Returns:
            True if the proof is valid.
        """
        current = leaf
        idx = leaf_index

        for sibling in proof:
            if idx % 2 == 0:
                current = _hash_pair(current, sibling)
            else:
                current = _hash_pair(sibling, current)
            idx = idx // 2

        return current == root


def compute_root(leaves: List[str]) -> str:
    """Convenience: build a tree and return the root."""
    tree = MerkleTree(leaves)
    return tree.root
