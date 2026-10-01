#!/usr/bin/env python3
"""Saakshi Independent Custody Ledger Verifier CLI.

Purpose: Standalone verification tool to cryptographically audit an append-only custody chain.
Inputs: Path to JSONL custody log file.
Outputs: Exit code 0 on verified chain; non-zero with diagnostic error on tampering.
Status: Implemented
"""

import argparse
import json
import sys
from pathlib import Path

# Add backend to path to import verify_chain and compute_entry_hash if available,
# or provide standalone implementation so this script runs with zero dependencies.


def compute_entry_hash(
    index: int,
    timestamp: str,
    actor: str,
    action: str,
    evidence_id: str,
    evidence_hash: str,
    previous_hash: str,
    details: dict,
) -> str:
    import hashlib

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


def verify_custody_file(file_path: Path | str) -> tuple[bool, int, str | None]:
    """Verify JSONL custody file.

    Returns:
        (is_valid, record_count, error_message)
    """
    path = Path(file_path)
    if not path.is_file():
        return False, 0, f"File not found: {path}"

    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records.append(rec)
            except json.JSONDecodeError as err:
                return False, len(records), f"Malformed JSON at line {line_num}: {err}"

    if not records:
        return True, 0, None

    for i, rec in enumerate(records):
        idx = rec.get("index")
        if idx != i:
            return False, len(records), f"Index gap at block {i}: expected {i}, found {idx}"

        prev_hash = rec.get("previous_hash")
        if i == 0:
            if prev_hash != "0" * 64:
                return False, len(records), f"Genesis previous_hash is not 64 zeroes at block 0: {prev_hash}"
        else:
            prev_entry_hash = records[i - 1].get("entry_hash")
            if prev_hash != prev_entry_hash:
                return False, len(records), f"Broken chain link at block {i}: expected {prev_entry_hash}, got {prev_hash}"

        expected_hash = compute_entry_hash(
            index=rec.get("index", 0),
            timestamp=rec.get("timestamp", ""),
            actor=rec.get("actor", ""),
            action=rec.get("action", ""),
            evidence_id=rec.get("evidence_id", ""),
            evidence_hash=rec.get("evidence_hash", ""),
            previous_hash=rec.get("previous_hash", ""),
            details=rec.get("details", {}),
        )

        entry_hash = rec.get("entry_hash", "")
        if entry_hash.lower() != expected_hash.lower():
            return (
                False,
                len(records),
                f"Tampering detected at block {i}: recorded {entry_hash} != computed {expected_hash}",
            )

    return True, len(records), None


def main() -> None:
    parser = argparse.ArgumentParser(description="Cryptographically verify Saakshi custody chain.")
    parser.add_argument("ledger_file", help="Path to custody_chain.jsonl file")
    args = parser.parse_args()

    valid, count, err = verify_custody_file(args.ledger_file)
    if valid:
        print(f"[OK] Custody chain VALID: {count} verified blocks with intact cryptographic links.")
        sys.exit(0)
    else:
        print(f"[FAIL] Custody chain COMPROMISED: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
