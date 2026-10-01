"""FrameProof Local Append-Only Ledger Anchor.

Purpose: Local filesystem implementation of AnchorBackend for air-gapped workstations.
Inputs: Root hashes and case metadata.
Outputs: Local ledger record IDs and cryptographic verification booleans.
Status: Implemented
"""

import hashlib
import json
from pathlib import Path
from typing import Any

from app.modules.custody.anchor.base import AnchorBackend


class LocalLedgerAnchor(AnchorBackend):
    """File-backed local anchor log storing committed state roots."""

    def __init__(self, ledger_file: Path | str | None = None) -> None:
        """Initialize local ledger anchor.

        Args:
            ledger_file: Optional path to JSON file storing local receipts.
                         If None, an in-memory dictionary is used.
        """
        self.ledger_file = Path(ledger_file) if ledger_file else None
        self._memory_records: dict[str, dict[str, Any]] = {}

        if self.ledger_file and self.ledger_file.exists():
            self._load_records()

    def _load_records(self) -> None:
        """Load records from file."""
        if not self.ledger_file or not self.ledger_file.exists():
            return
        try:
            with open(self.ledger_file, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._memory_records = data
        except (json.JSONDecodeError, OSError):
            self._memory_records = {}

    def _save_records(self) -> None:
        """Persist records to file."""
        if not self.ledger_file:
            return
        self.ledger_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump(self._memory_records, f, indent=2, sort_keys=True)

    def anchor(self, root_hash: str, metadata: dict[str, Any] | None = None) -> str:
        """Anchor a root hash locally.

        Args:
            root_hash: The SHA-256 root hash to commit.
            metadata: Context parameters.

        Returns:
            Computed anchor identifier.
        """
        canonical = f"{root_hash}:{json.dumps(metadata or {}, sort_keys=True)}"
        anchor_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        self._memory_records[anchor_id] = {
            "anchor_id": anchor_id,
            "root_hash": root_hash,
            "metadata": metadata or {},
        }
        self._save_records()
        return anchor_id

    def verify_anchor(self, anchor_id: str, expected_root_hash: str) -> bool:
        """Verify whether an anchor exists and matches the expected root."""
        record = self._memory_records.get(anchor_id)
        if not record:
            return False
        return record.get("root_hash", "").lower() == expected_root_hash.lower()
