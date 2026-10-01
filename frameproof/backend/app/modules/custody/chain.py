"""FrameProof Append-Only Hash-Chained Custody Log.

Purpose: Provide an immutable, tamper-evident cryptographic audit log for all evidence lifecycle events.
Inputs: Action descriptors, actor credentials, evidence identifiers, and cryptographic digests.
Outputs: Hash-chained audit log records and tamper verification diagnostic reports.
Status: Implemented
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

GENESIS_PREVIOUS_HASH = "0" * 64


class CustodyRecord(BaseModel):
    """Immutable entry in the cryptographic chain of custody."""

    index: int = Field(ge=0, description="Sequential monotonic block index")
    timestamp: str = Field(description="ISO 8601 UTC timestamp")
    actor: str = Field(description="Forensic investigator badge / system component ID")
    action: str = Field(description="Lifecycle operation performed")
    evidence_id: str = Field(description="Unique identifier of target evidence artifact")
    evidence_hash: str = Field(description="SHA-256 hash of the evidence at this stage")
    previous_hash: str = Field(description="Cryptographic hash of the previous custody record")
    details: dict[str, Any] = Field(default_factory=dict, description="Operational parameters")
    entry_hash: str = Field(description="SHA-256 digest over the canonical record content")


def compute_entry_hash(
    index: int,
    timestamp: str,
    actor: str,
    action: str,
    evidence_id: str,
    evidence_hash: str,
    previous_hash: str,
    details: dict[str, Any],
) -> str:
    """Compute deterministic SHA-256 digest over canonical JSON representation."""
    canonical_payload = {
        "action": action,
        "actor": actor,
        "details": details,
        "evidence_hash": evidence_hash,
        "evidence_id": evidence_id,
        "index": index,
        "previous_hash": previous_hash,
        "timestamp": timestamp,
    }
    serialized = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def verify_chain(chain: list[CustodyRecord]) -> tuple[bool, str | None]:
    """Verify cryptographic integrity of an entire custody log chain.

    Args:
        chain: List of sequential CustodyRecord instances.

    Returns:
        Tuple of (is_valid: bool, error_message: str | None).
    """
    if not chain:
        return True, None

    for i, record in enumerate(chain):
        # 1. Verify sequence index
        if record.index != i:
            return False, f"Sequence gap at block {i}: expected index {i}, found {record.index}"

        # 2. Verify genesis block linkage
        if i == 0:
            if record.previous_hash != GENESIS_PREVIOUS_HASH:
                return False, f"Invalid genesis block previous_hash: expected '{GENESIS_PREVIOUS_HASH}', found '{record.previous_hash}'"
        else:
            prev_record = chain[i - 1]
            if record.previous_hash != prev_record.entry_hash:
                return (
                    False,
                    f"Broken hash link at block {i}: expected '{prev_record.entry_hash}', found '{record.previous_hash}'",
                )

        # 3. Verify internal payload integrity against entry_hash
        expected_hash = compute_entry_hash(
            index=record.index,
            timestamp=record.timestamp,
            actor=record.actor,
            action=record.action,
            evidence_id=record.evidence_id,
            evidence_hash=record.evidence_hash,
            previous_hash=record.previous_hash,
            details=record.details,
        )

        if record.entry_hash.lower() != expected_hash.lower():
            return (
                False,
                f"Tampering detected at block {i}: stored entry_hash '{record.entry_hash}' does not match computed '{expected_hash}'",
            )

    return True, None


class CustodyLog:
    """Manager for appending and persisting custody records."""

    def __init__(self, log_path: Path | str | None = None) -> None:
        """Initialize custody log."""
        self.log_path = Path(log_path) if log_path else None
        self.records: list[CustodyRecord] = []

        if self.log_path and self.log_path.exists():
            self.load()

    def append(
        self,
        actor: str,
        action: str,
        evidence_id: str,
        evidence_hash: str,
        details: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> CustodyRecord:
        """Append a new verified record to the custody chain."""
        index = len(self.records)
        previous_hash = self.records[-1].entry_hash if self.records else GENESIS_PREVIOUS_HASH

        ts = (timestamp or datetime.now(UTC)).isoformat()
        payload_details = details or {}

        entry_hash = compute_entry_hash(
            index=index,
            timestamp=ts,
            actor=actor,
            action=action,
            evidence_id=evidence_id,
            evidence_hash=evidence_hash,
            previous_hash=previous_hash,
            details=payload_details,
        )

        record = CustodyRecord(
            index=index,
            timestamp=ts,
            actor=actor,
            action=action,
            evidence_id=evidence_id,
            evidence_hash=evidence_hash,
            previous_hash=previous_hash,
            details=payload_details,
            entry_hash=entry_hash,
        )

        self.records.append(record)
        if self.log_path:
            self._save_record_to_file(record)

        return record

    def _save_record_to_file(self, record: CustodyRecord) -> None:
        """Append line to jsonl file."""
        if not self.log_path:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")

    def load(self) -> None:
        """Load records from jsonl file and verify chain integrity."""
        if not self.log_path or not self.log_path.exists():
            return

        loaded_records: list[CustodyRecord] = []
        with open(self.log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    loaded_records.append(CustodyRecord.model_validate_json(line))

        valid, err = verify_chain(loaded_records)
        if not valid:
            raise ValueError(f"Custody file integrity violation: {err}")

        self.records = loaded_records

    def verify(self) -> tuple[bool, str | None]:
        """Verify the currently loaded custody chain."""
        return verify_chain(self.records)
