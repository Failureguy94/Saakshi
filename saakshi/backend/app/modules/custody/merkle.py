"""Saakshi Merkle Tree & Inclusion Proof Engine.

Purpose: Construct cryptographic Merkle trees over video segment hashes,
         calculate verifiable roots, and generate/verify inclusion proofs.
Inputs: List of cryptographic leaf hashes (e.g., frame or segment digests).
Outputs: Merkle root string, inclusion proof audit paths, and boolean verification results.
Status: Implemented
"""

import hashlib
from typing import NamedTuple


class ProofStep(NamedTuple):
    """Single step in a Merkle inclusion proof."""

    sibling_hash: str
    is_left: bool  # True if sibling is on the left, False if on the right


def _hash_leaf(leaf_hex: str) -> str:
    """Hash leaf with RFC 6962 domain separation prefix 0x00."""
    raw = bytes.fromhex(leaf_hex) if len(leaf_hex) % 2 == 0 else leaf_hex.encode("utf-8")
    return hashlib.sha256(b"\x00" + raw).hexdigest()


def _hash_nodes(left_hex: str, right_hex: str) -> str:
    """Hash two internal nodes with RFC 6962 domain separation prefix 0x01."""
    left_bytes = bytes.fromhex(left_hex)
    right_bytes = bytes.fromhex(right_hex)
    return hashlib.sha256(b"\x01" + left_bytes + right_bytes).hexdigest()


class MerkleTree:
    """Cryptographic Merkle tree implementation supporting inclusion proofs."""

    def __init__(self, leaf_hashes: list[str]) -> None:
        """Initialize and construct Merkle tree from raw leaf hashes.

        Args:
            leaf_hashes: List of hexadecimal hash strings representing evidence chunks.

        Raises:
            ValueError: If leaf_hashes is empty.
        """
        if not leaf_hashes:
            raise ValueError("Cannot construct a Merkle tree with empty leaves.")

        self.raw_leaves = list(leaf_hashes)
        self.levels: list[list[str]] = []
        self._build_tree()

    def _build_tree(self) -> None:
        """Construct bottom-up tree levels."""
        current_level = [_hash_leaf(lh) for lh in self.raw_leaves]
        self.levels.append(current_level)

        while len(current_level) > 1:
            next_level: list[str] = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                next_level.append(_hash_nodes(left, right))
            current_level = next_level
            self.levels.append(current_level)

    @property
    def root(self) -> str:
        """Return the root hash of the Merkle tree."""
        return self.levels[-1][0]

    def get_proof(self, index: int) -> list[ProofStep]:
        """Generate cryptographic audit path (inclusion proof) for a given leaf index.

        Args:
            index: Zero-based leaf index.

        Returns:
            List of ProofStep tuples containing sibling hash and relative position.

        Raises:
            IndexError: If index is out of bounds.
        """
        if index < 0 or index >= len(self.raw_leaves):
            raise IndexError(f"Leaf index {index} out of range [0, {len(self.raw_leaves) - 1}].")

        proof: list[ProofStep] = []
        current_idx = index

        # Traverse up from leaves to the level below root
        for level in self.levels[:-1]:
            if current_idx % 2 == 0:
                # Leaf is left; sibling is right
                sibling_idx = current_idx + 1 if current_idx + 1 < len(level) else current_idx
                is_left = False
            else:
                # Leaf is right; sibling is left
                sibling_idx = current_idx - 1
                is_left = True

            sibling_hash = level[sibling_idx]
            proof.append(ProofStep(sibling_hash=sibling_hash, is_left=is_left))
            current_idx //= 2

        return proof

    @staticmethod
    def verify_proof(
        leaf_hash: str,
        proof: list[ProofStep],
        expected_root: str,
    ) -> bool:
        """Verify an inclusion proof against an expected Merkle root.

        Args:
            leaf_hash: The raw leaf hash string being verified.
            proof: The audit path returned by get_proof.
            expected_root: The expected root hash to verify against.

        Returns:
            True if leaf is cryptographically proven to be in the tree, False otherwise.
        """
        current_hash = _hash_leaf(leaf_hash)

        for step in proof:
            if step.is_left:
                current_hash = _hash_nodes(step.sibling_hash, current_hash)
            else:
                current_hash = _hash_nodes(current_hash, step.sibling_hash)

        return current_hash.lower() == expected_root.lower()
