# Standard Operating Procedure (SOP): Cryptographic Chain of Custody

## 1. Purpose
Define the protocol for maintaining, auditing, and cryptographically anchoring the chain of custody for all surveillance digital evidence processed within FrameProof.

## 2. Requirements
- Every action performed on an evidence artifact must be cryptographically bound to:
  - Previous Block Hash (Tamper-evident hash chain).
  - Actor Identity (Investigator Badge / User ID).
  - Action Identifier (`ACQUISITION`, `INDEX_PARSE`, `CARVE`, `TIMELINE_SYNC`, `EXPORT`).
  - Target Evidence Hash (SHA-256).
  - High-precision UTC Timestamp.

## 3. Audit Procedure
1. Prior to report generation, run `scripts/verify_ledger.py` or the platform's verification engine.
2. Ensure that every segment's Merkle inclusion proof verifies against the segment's recorded root.
3. Validate that no previous block hash discrepancies or chronological anomalies exist in the chain log.
4. Export the verified chain certificate alongside the final case bundle.
