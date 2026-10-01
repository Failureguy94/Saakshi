"""Unit tests for Merkle tree and cryptographic inclusion proofs."""

import hashlib

import pytest

from app.modules.custody.merkle import MerkleTree


def test_merkle_empty_raises() -> None:
    with pytest.raises(ValueError):
        MerkleTree([])


def test_merkle_single_leaf() -> None:
    leaf = hashlib.sha256(b"frame_0").hexdigest()
    tree = MerkleTree([leaf])
    assert len(tree.root) == 64

    proof = tree.get_proof(0)
    assert len(proof) == 0
    assert MerkleTree.verify_proof(leaf, proof, tree.root) is True


def test_merkle_even_leaves() -> None:
    leaves = [hashlib.sha256(f"frame_{i}".encode()).hexdigest() for i in range(4)]
    tree = MerkleTree(leaves)

    assert len(tree.root) == 64

    for i, leaf in enumerate(leaves):
        proof = tree.get_proof(i)
        assert MerkleTree.verify_proof(leaf, proof, tree.root) is True

    # Tampered leaf should fail
    tampered_leaf = hashlib.sha256(b"tampered").hexdigest()
    assert MerkleTree.verify_proof(tampered_leaf, tree.get_proof(0), tree.root) is False


def test_merkle_odd_leaves() -> None:
    leaves = [hashlib.sha256(f"frame_{i}".encode()).hexdigest() for i in range(5)]
    tree = MerkleTree(leaves)

    for i, leaf in enumerate(leaves):
        proof = tree.get_proof(i)
        assert MerkleTree.verify_proof(leaf, proof, tree.root) is True


def test_merkle_proof_out_of_bounds() -> None:
    tree = MerkleTree(["aa" * 32, "bb" * 32])
    with pytest.raises(IndexError):
        tree.get_proof(5)
    with pytest.raises(IndexError):
        tree.get_proof(-1)
