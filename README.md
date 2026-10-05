# Saakshi

### Vendor-Agnostic DVR/NVR Forensic Platform for Acquisition, Recovery & Analysis

Saakshi is a forensic analysis platform designed to provide a unified workflow for investigating surveillance evidence from DVR/NVR systems.

The project addresses a common forensic problem: surveillance systems use vendor-specific formats, fragmented tooling, proprietary indexes, overwritten footage, and unreliable timestamps. Saakshi brings acquisition, identification, parsing, recovery, timeline analysis, integrity verification, and reporting into one workflow.

> **Important:** The current repository is a reproducible prototype/demonstrator. The data, DVR image, recovered footage, and model/results used in the demonstration are synthetic. The implementation should not be interpreted as universal support for arbitrary real-world DVR/NVR formats.

---

## Problem

Traditional DVR/NVR forensic workflows are often fragmented:

- **Proprietary formats** — every OEM can use its own filesystem, index, and video container.
- **Tool fragmentation** — investigators may need different vendor-specific tools for different devices.
- **Deleted footage** — orphaned or overwritten H.264 segments may no longer appear in the normal index.
- **Untrusted timestamps** — DVR clocks can drift and make cross-camera reconstruction difficult.
- **Weak custody trails** — manual evidence handling makes integrity verification harder.
- **Disconnected analysis** — footage, recovery results, integrity information, and reports are often handled separately.

Saakshi aims to turn this into a single evidence-processing pipeline.

---

## Core Workflow

```text
Evidence
   │
   ▼
Identification
   │
   ▼
Acquisition & Hashing
   │
   ▼
Parsing
   │
   ▼
Recovery / NAL Carving
   │
   ▼
Timeline Analysis
   │
   ▼
Video Analytics
   │
   ▼
Chain of Custody
   │
   ▼
Integrity / Tamper Verification
   │
   ▼
Forensic Report
```

---

## What is implemented

The current prototype demonstrates an end-to-end synthetic DVR forensic workflow.

### 1. DVR/OEM Identification

The prototype supports profile-based identification for the synthetic **VendorX** format.

The architecture is designed around declarative format profiles so that additional OEM formats can be added without rewriting the complete forensic pipeline.

### 2. Evidence Acquisition & Hashing

The acquisition stage generates forensic hashes for the evidence:

- MD5
- SHA-256

These hashes are used throughout the evidence workflow to maintain integrity.

### 3. DVR Parsing

The parser extracts indexed recording segments from the synthetic VendorX DVR index.

This demonstrates the profile-driven approach to understanding a proprietary DVR structure.

### 4. Deleted Footage Recovery

Saakshi supports two recovery paths in the prototype:

- Indexed segment extraction
- Naive NAL-based carving for deleted/orphaned H.264 streams

The demonstration intentionally contains an orphaned H.264 segment so that the recovery workflow can be reproduced.

### 5. H.264 / GOP Reconstruction

The recovery pipeline includes NAL-level processing and GOP repair to reconstruct recoverable H.264 footage.

### 6. Timeline Analysis

The prototype includes DVR timeline offset estimation.

The current implementation uses a mock/synthetic offset rather than claiming full real-world timestamp synchronization.

### 7. Video Analytics

The current analytics module performs basic motion detection using OpenCV frame differences.

Future versions can extend this layer with object detection, OCR, and cross-camera event correlation.

### 8. Chain of Custody

Saakshi maintains an append-only custody trail using a SQLite-backed hash chain.

Each custody entry is linked to the previous entry, allowing the chain to be verified.

### 9. Merkle-Based Evidence Manifest

The platform creates a manifest containing hashes of the evidence image and recovered/processed clips.

A Merkle tree is used to produce an integrity root for the evidence set.

### 10. Tamper Detection

The prototype includes a reproducible tamper test:

```text
Original clip
     │
     ▼
Create manifest
     │
     ▼
Modify clip
     │
     ▼
Verify manifest
     │
     └──► Hash mismatch detected
```

The original clip can then be restored and the manifest verified again.

### 11. Forensic Report

Saakshi generates a PDF evidence report using ReportLab.

The report includes an evidence/integrity workflow and a BSA 2023 Section 63-oriented compliance section.

---

## Demonstration

The demo uses a synthetic DVR image containing:

- Indexed surveillance footage
- An intentionally orphaned/deleted H.264 segment
- A controlled DVR timestamp offset
- Synthetic motion events
- Evidence hashes
- A custody history
- A Merkle manifest
- A controlled tamper scenario

This makes the entire workflow reproducible without requiring access to a physical commercial DVR/NVR during development.

---

## Architecture

```text
                    ┌──────────────────────────┐
                    │      DVR / NVR Evidence  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Identification Engine  │
                    │   Format Profile Matching │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Acquisition & Hashing     │
                    │ MD5 + SHA-256             │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Format Profile / Parser  │
                    │ Indexed Segment Parsing   │
                    └────────────┬─────────────┘
                                 │
                         ┌───────┴────────┐
                         ▼                ▼
                ┌────────────────┐ ┌─────────────────┐
                │ Indexed        │ │ NAL / H.264     │
                │ Recovery       │ │ Carving         │
                └───────┬────────┘ └────────┬────────┘
                        └─────────┬─────────┘
                                  ▼
                    ┌──────────────────────────┐
                    │ Timeline / Video Analysis│
                    │ OpenCV Motion Detection  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Integrity & Custody      │
                    │ Hash Chain + Merkle Tree │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Court-Ready Report       │
                    │ PDF + Evidence Manifest  │
                    └──────────────────────────┘
```

---

## Project Structure

```text
Saakshi/
├── demo_server/
│   └── main.py
│
├── saakshi/
│   ├── engine/
│   │   ├── nal_carver.py
│   │   └── gop_repair.py
│   │
│   ├── modules/
│   │   ├── acquisition/
│   │   ├── analytics/
│   │   ├── custody/
│   │   ├── parsing/
│   │   ├── recovery/
│   │   ├── reporting/
│   │   └── timeline/
│   │
│   └── frontend/
│       └── src/
│           ├── pages/
│           ├── App.tsx
│           ├── Card.tsx
│           └── store.ts
│
├── scripts/
│   └── run_demo.py
│
├── start_demo.py
├── requirements.txt
└── README.md
```

---

## Technology Stack

### Backend / Forensics

- Python
- OpenCV
- FFmpeg
- ReportLab
- SQLite
- H.264 / NAL processing

### Frontend

- React
- TypeScript
- Vite-based frontend tooling

### Evidence Integrity

- MD5
- SHA-256
- Append-only hash chain
- Merkle tree

---

## Running the Demonstration

### 1. Clone the repository

```bash
git clone <repository-url>
cd Saakshi
```

### 2. Initialize the environment

The repository includes the required Python dependencies in:

```text
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

### 3. Run the synthetic forensic pipeline

```bash
python scripts/run_demo.py
```

The demonstration pipeline performs the following stages:

```text
Initialize database
        ↓
Generate synthetic DVR evidence
        ↓
Identify format
        ↓
Acquire + hash
        ↓
Parse indexed recordings
        ↓
Recover / carve H.264
        ↓
Estimate timeline
        ↓
Run motion analytics
        ↓
Create custody records
        ↓
Create Merkle manifest
        ↓
Run tamper verification
        ↓
Restore evidence
        ↓
Generate forensic report
```

### 4. Start the demonstration UI

```bash
python start_demo.py
```

The project includes a React-based forensic interface for exploring the workflow.

---

## Integrity Verification

Saakshi treats evidence integrity as a first-class part of the workflow.

A simplified verification flow is:

```text
Evidence
   │
   ├── SHA-256
   ├── MD5
   │
   ▼
Custody Entry
   │
   ├── Previous Hash
   └── Entry Hash
   │
   ▼
Merkle Manifest
   │
   └── Merkle Root
```

If a recovered clip is modified after the manifest is created, verification detects the changed hash.

This provides a reproducible demonstration of tamper-evident evidence handling.

---

## Why Saakshi?

Saakshi is built around the idea that surveillance forensics should not stop at **recovering a video**.

A useful forensic system should also answer:

- Where did the evidence come from?
- What format was it?
- What was recovered?
- Was the recovered data modified?
- Can the evidence history be verified?
- What timestamps and processing steps were applied?
- Can the findings be exported as a structured evidence report?

The prototype demonstrates this complete workflow from evidence acquisition to reporting.

---

## Roadmap

The current implementation is a prototype. The broader Saakshi architecture is intended to evolve toward:

- Real-world multi-OEM format profiles
- Blind format discovery
- Advanced deleted-footage and slack-space recovery
- Ring-buffer reconstruction
- Accurate PTS/DVR clock synchronization
- OCR-based timestamp extraction
- Confidence-scored temporal normalization
- Object and face detection
- Cross-camera event correlation
- Advanced video tampering detection
- Larger-scale evidence storage
- Permissioned ledger anchoring
- Expanded court/evidence-pack generation
- Offline-first forensic deployment

These are architectural targets and should not be interpreted as features already implemented in the current repository.

---

## SIH 2026

**Smart India Hackathon 2026**

- **Problem Statement:** SIH26150
- **Problem:** Development of a Multi-Vendor DVR/NVR Forensic Analysis Tool for Standardized Acquisition, Recovery, and Analysis of Surveillance Evidence
- **Team:** Fsociety
- **Team ID:** 155347
- **Project:** Saakshi

---

## Disclaimer

Saakshi is a research and hackathon prototype.

The current demonstration uses synthetic evidence and controlled test conditions. Results from the prototype should not be treated as validated forensic conclusions for real investigations.

Real-world forensic deployment requires validation against actual DVR/NVR devices, proprietary formats, acquisition procedures, evidence-handling standards, and applicable legal requirements.

---

## Team

Built by **Team Fsociety** for **Smart India Hackathon 2026**.

> **Saakshi — recovering evidence is only the beginning. Proving it is what matters.**
