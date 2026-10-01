"""Saakshi Custody Anchoring Interface.

Purpose: Abstract contract for external cryptographic ledger anchoring (Local, Hyperledger Fabric, etc.).
Inputs: Merkle root hashes and forensic metadata.
Outputs: Anchor receipt identifiers and verification states.
Status: Implemented
"""

from abc import ABC, abstractmethod
from typing import Any


class AnchorBackend(ABC):
    """Abstract interface for anchoring custody state to a persistent or distributed ledger."""

    @abstractmethod
    def anchor(self, root_hash: str, metadata: dict[str, Any] | None = None) -> str:
        """Anchor a Merkle root or chain head to the target backend.

        Args:
            root_hash: The SHA-256 root hash to commit.
            metadata: Additional contextual forensic parameters.

        Returns:
            Receipt or transaction identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_anchor(self, anchor_id: str, expected_root_hash: str) -> bool:
        """Verify whether an anchor matches the recorded root.

        Args:
            anchor_id: Identifier of the anchor receipt.
            expected_root_hash: Expected SHA-256 root hash.

        Returns:
            True if anchor exists and matches; False otherwise.
        """
        raise NotImplementedError
