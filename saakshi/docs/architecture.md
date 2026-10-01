# Saakshi Architecture & Forensic Data Flow

Saakshi is an air-gapped, vendor-agnostic DVR/NVR digital forensics platform designed for Smart India Hackathon 2026 (PS SIH26150, NTRO). It standardizes proprietary, corrupt, or raw surveillance disk images into court-admissible forensic evidence complying with Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA) / Section 65B of Indian Evidence Act (IEA).

---

## 1. High-Level Modular Architecture

```mermaid
flowchart TD
    subgraph Evidence_Layer ["Forensic Physical / Storage Layer"]
        RAW["Raw DD / E01 / Physical Disk (/dev/sdX)"]
        CAP["Network / ONVIF Packet Capture"]
    end

    subgraph Core_Pipeline ["Saakshi Forensic Engine"]
        direction TB

        subgraph S1 ["Stage 1: Acquisition & Ingestion"]
            HASH["Dual Streaming Hasher (MD5 + SHA-256)"]
            IMAGER["Write-Blocked Imager / Reader"]
        end

        subgraph S2 ["Stage 2: Identification & OEM Profiling"]
            FP["Filesystem & Magic Fingerprinter"]
            PROF["OEM Profile Engine (YAML Rules)"]
        end

        subgraph S3 ["Stage 3: Parsing & Deconstruction"]
            FS_PARSER["Proprietary FS Parser (DHFS, HIKFS, etc.)"]
            IDX_PARSER["Index Table & Metadata Extractor"]
            DEMUX["Container Demuxer (DHAV, PES, MP4)"]
        end

        subgraph S4 ["Stage 4: Carving & Stream Recovery"]
            NAL_CARVE["Annex-B NAL Carver (H.264 / H.265)"]
            RING["Ring Buffer Overwrite Recovery"]
            ORPHAN["Slack & Unallocated Sector Harvester"]
            GOP["GOP Repair & SPS/PPS Reconstructor"]
        end

        subgraph S5 ["Stage 5: Timeline, Sync & Trust"]
            OSD["OSD / Watermark OCR Engine"]
            DRIFT["RTC Drift & Clock Skew Corrector"]
            TRUST["Multi-Camera Temporal Trust Engine"]
        end

        subgraph S6 ["Stage 6: Analytics & Tamper Detection"]
            TAMPER["Frame Integrity & Tamper Detector"]
            EVENT["Cross-Camera Event Graph"]
            MOTION["Motion & Trajectory Vector Analyzer"]
        end

        subgraph S7 ["Stage 7: Cryptographic Custody"]
            CHAIN["Append-Only Hash-Chained Audit Ledger"]
            MERKLE["Segment Merkle Tree & Inclusion Proofs"]
            ANCHOR["Ledger Anchor (Local / Hyperledger Fabric)"]
        end
    end

    subgraph Court_Output ["Admissible Reporting Layer"]
        REP["Court-Ready Forensic Report Builder"]
        CERT["Section 63 BSA / 65B IEA Certificate"]
        VERIFY["Cryptographic Verification Bundle"]
    end

    RAW --> IMAGER
    CAP --> IMAGER
    IMAGER --> HASH
    HASH --> FP
    FP --> PROF
    PROF --> FS_PARSER
    PROF --> IDX_PARSER
    FS_PARSER --> DEMUX
    IDX_PARSER --> DEMUX
    RAW -. "Read-Only Carve" .-> NAL_CARVE
    RAW -. "Read-Only Carve" .-> ORPHAN
    NAL_CARVE --> GOP
    ORPHAN --> GOP
    RING --> GOP
    DEMUX --> TRUST
    GOP --> TRUST
    OSD --> DRIFT
    DRIFT --> TRUST
    TRUST --> TAMPER
    TAMPER --> EVENT
    EVENT --> MOTION

    %% Custody tracking from all stages
    S1 -. "Custody Event" .-> CHAIN
    S2 -. "Custody Event" .-> CHAIN
    S3 -. "Custody Event" .-> CHAIN
    S4 -. "Custody Event" .-> CHAIN
    S5 -. "Custody Event" .-> CHAIN
    S6 -. "Custody Event" .-> CHAIN
    CHAIN --> MERKLE
    MERKLE --> ANCHOR

    MOTION --> REP
    ANCHOR --> CERT
    REP --> CERT
    CERT --> VERIFY
```

---

## 2. End-to-End Forensic Data Flow: Disk to Court

```mermaid
sequenceDiagram
    autonumber
    actor Officer as Forensic Investigator
    participant HW as Physical Storage (Write-Blocked)
    participant Core as Saakshi Engine
    participant Ledger as Custody Ledger (Hash-Chained)
    participant Court as Judicial Bench / Court

    Officer->>HW: Connect disk via hardware write-blocker
    Officer->>Core: Initiate evidence intake (Case ID, Officer ID)
    Core->>HW: Stream raw bytes (Read-Only)
    Core->>Core: Compute MD5 & SHA-256 simultaneously
    Core->>Ledger: Log Acquisition Event (Image Hash, Timestamp, Officer)
    
    Core->>Core: Fingerprint filesystem signatures & OEM profile
    Core->>Core: Parse proprietary indexes & carve unallocated sectors
    Core->>Core: Reconstruct GOPs, NAL units, and frame timestamps
    Core->>Ledger: Log Recovery & Carving Merkle Root
    
    Core->>Core: Cross-validate OSD OCR timestamps against frame headers
    Core->>Core: Formulate Unified Evidence Model (Device -> Channel -> Segment -> Frame)
    Core->>Ledger: Log Timeline Harmonization & Final Video Merkle Roots
    
    Officer->>Core: Request forensic report generation
    Core->>Ledger: Verify chain integrity (no tampering detected)
    Core->>Core: Generate Section 63 BSA / 65B IEA Certificate + PDF Report
    Core->>Court: Produce export package: Clean Video + Merkle Proof + Signed Audit Trail
    Court->>Court: Independent ledger verification (zero-trust audit)
```

---

## 3. Guarantees & Constraints
1. **Strict Read-Only Access**: All intake modules enforce OS read-only open flags (`O_RDONLY`).
2. **Deterministic Cryptographic Chain**: Every evidence modification or analysis produces an immutable audit record in the custody chain.
3. **Air-Gapped Operation**: Zero outbound dependencies, telemetry, or external API calls.
