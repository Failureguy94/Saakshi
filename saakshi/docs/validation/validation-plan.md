# Saakshi Scientific Forensic Validation Plan

## 1. Overview
In accordance with ASTM E3016 (Standard Guide for Establishing Confidence in Digital Forensics Methods) and SWGDE (Scientific Working Group on Digital Evidence) standards, Saakshi validation is conducted against controlled synthetic ground-truth test data and physical lab drives.

## 2. Test Suites
- **Hashing Validation**:
  - Verification against NIST Known Hash Datasets (NSRL) and zero-length / edge-case files.
  - Streaming chunk equivalence check (chunked vs monolithic).
- **Annex-B NAL Carver Validation**:
  - Synthetic images injected with deterministically positioned H.264 / H.265 NAL units at odd byte offsets.
  - Recovery accuracy, precision, and false-positive measurement under high-entropy pseudo-random noise.
- **Merkle Tree & Custody Chain**:
  - Tamper detection tests simulating single-bit mutations in historical custody records.
  - Verification of inclusion proofs across arbitrary power-of-two and odd leaf sizes.
- **Section 63 BSA Compliance Verification**:
  - Legal admissibility stress tests validating formatting and required statutory fields.
