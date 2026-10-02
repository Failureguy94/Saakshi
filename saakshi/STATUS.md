# Saakshi Submissions & Modules Forensic Honesty Matrix (STATUS.md)

This document provides a transparent, accountable status for every module in the **Saakshi** repository (Smart India Hackathon 2026, Problem Statement SIH26150, NTRO). No module claims functionality beyond its verified implementation status.

| Module Path | Architectural Purpose | Status | Test Coverage |
| :--- | :--- | :--- | :--- |
| **`acquisition/hashing.py`** | Streaming dual MD5 + SHA-256 single-pass hasher | **IMPLEMENTED** | `tests/unit/test_hashing.py` (100%) |
| **`acquisition/cli.py`** | `saakshi acquire` / `verify` CLI — read-only hash + custody log | **IMPLEMENTED** | `tests/unit/test_acquisition_cli.py` (100%) |
| **`acquisition/imager.py`** | Hardware write-blocked bit-stream imager | **STUB** | N/A (raises `NotImplementedError`) |
| **`acquisition/readers/raw.py`** | Random-access raw bit-stream reader | **STUB** | N/A (raises `NotImplementedError`) |
| **`acquisition/readers/e01.py`** | EnCase E01 decompressor and parser | **STUB** | N/A (raises `NotImplementedError`) |
| **`acquisition/readers/network_onvif.py`** | Live RTSP/ONVIF packet capture | **STUB** | N/A (raises `NotImplementedError`) |
| **`custody/merkle.py`** | Cryptographic Merkle tree & inclusion proofs | **IMPLEMENTED** | `tests/unit/test_merkle.py` (100%) |
| **`custody/chain.py`** | Append-only hash-chained custody log & verifier | **IMPLEMENTED** | `tests/unit/test_custody_chain.py` (100%) |
| **`custody/anchor/base.py`** | Abstract anchoring contract | **IMPLEMENTED** | `tests/unit/test_custody_chain.py` |
| **`custody/anchor/local_ledger.py`** | Local filesystem / in-memory anchor backend | **IMPLEMENTED** | `tests/unit/test_custody_chain.py` (100%) |
| **`custody/anchor/fabric.py`** | Hyperledger Fabric consortium anchor | **STUB** | `tests/unit/test_custody_chain.py` (raises `NotImplementedError`) |
| **`custody/decorators.py`** | Read-only enforcement & custody stage tracking | **IMPLEMENTED** | Enforces OS read-only guarantees |
| **`profiles/schema.py`** | Pydantic v2 OEM vendor profile schema | **IMPLEMENTED** | `tests/unit/test_profiles.py` (100%) |
| **`profiles/loader.py`** | Multi-vendor YAML loader and validator | **IMPLEMENTED** | `tests/unit/test_profiles.py` (100%) |
| **`profiles/engine.py`** | Heuristic profile matching engine | **STUB** | N/A (raises `NotImplementedError`) |
| **`profiles/vendors/*.yaml`** (9 files) | Dahua, Hikvision, CP Plus, Uniview, TP-Link, Honeywell, Godrej, Matrix, Generic | **PLACEHOLDER SKELETONS** | `tests/unit/test_profiles.py` (Validated, marked `status: placeholder`) |
| **`recovery/nal_carver.py`** | Annex-B H.264/H.265 NAL start code carver + GOP grouping + SegmentRecord | **IMPLEMENTED** | `tests/unit/test_nal_carver.py` + `test_nal_carver_gops.py` (100% vs synthetic ground truth) |
| **`recovery/gop_repair.py`** | GOP reconstruction — borrows SPS/PPS from nearest valid neighbour | **IMPLEMENTED** | `tests/unit/test_gop_repair.py` (100%) |
| **`recovery/export.py`** | Remux recovered segments to .mp4 via ffmpeg -c copy; custody entries | **IMPLEMENTED** | `tests/unit/test_export.py` (100%; ffmpeg paths mocked) |
| **`recovery/index_guided.py`** | Video extraction via index pointers | **STUB** | N/A (raises `NotImplementedError`) |
| **`recovery/orphan_slack.py`** | Unallocated slack sector harvester | **STUB** | N/A (raises `NotImplementedError`) |
| **`recovery/ring_buffer.py`** | FIFO wrap-around overwrite boundary analyzer | **STUB** | N/A (raises `NotImplementedError`) |
| **`recovery/blind_discovery.py`** | Blind stream discovery and clustering | **STUB** | N/A (raises `NotImplementedError`) |
| **`parsing/filesystem.py`** | Proprietary DVR filesystem parser | **STUB** | N/A (raises `NotImplementedError`) |
| **`parsing/index_parser.py`** | Proprietary DVR recording index parser | **STUB** | N/A (raises `NotImplementedError`) |
| **`parsing/container_decoder.py`** | DHAV, HIK-PES container demuxer | **STUB** | N/A (raises `NotImplementedError`) |
| **`timeline/trust_engine.py`** | Multi-source temporal trust engine | **STUB** | N/A (raises `NotImplementedError`) |
| **`timeline/osd_ocr.py`** | Visual OSD timestamp OCR extractor | **STUB** | N/A (raises `NotImplementedError`) |
| **`timeline/drift.py`** | Hardware RTC drift & clock skew model | **STUB** | N/A (raises `NotImplementedError`) |
| **`timeline/camera_sync.py`** | Multi-camera temporal matrix synchronizer | **STUB** | N/A (raises `NotImplementedError`) |
| **`analytics/motion.py`** | Motion vector & macroblock activity analyzer | **STUB** | N/A (raises `NotImplementedError`) |
| **`analytics/objects.py`** | Offline neural network object detector | **STUB** | N/A (raises `NotImplementedError`) |
| **`analytics/faces.py`** | Facial feature extractor & re-identification | **STUB** | N/A (raises `NotImplementedError`) |
| **`analytics/event_graph.py`** | Spatiotemporal causal event graph builder | **STUB** | N/A (raises `NotImplementedError`) |
| **`analytics/tamper.py`** | Camera occlusion & frame tamper detector | **STUB** | N/A (raises `NotImplementedError`) |
| **`reporting/builder.py`** | Forensic court dossier compiler | **STUB** | N/A (raises `NotImplementedError`) |
| **`reporting/sec63_certificate.py`** | Section 63 BSA legal certificate generator | **STUB** | N/A (raises `NotImplementedError`) |
| **`api/health.py`** | Service health & air-gap verification endpoint | **IMPLEMENTED** | `tests/unit/test_api.py` (100%) |
| **`api/cases.py`** | Case registration & retrieval CRUD (SQLAlchemy/Postgres) | **IMPLEMENTED** | `tests/unit/test_api.py` (100%) |
| **`api/{devices,evidence,recovery,timeline,analytics,ledger,reports}.py`** | Pipeline API routers | **STUBS** | Routers mounted and typed |
| **`frontend`** | React + TypeScript + Vite + TailwindCSS UI | **IMPLEMENTED** | All 7 pages & navigation working, builds via Vite |
| **`scripts/make_synthetic_image.py`** | Original minimal synthetic disk generator with ground truth | **IMPLEMENTED** | Generates verified Annex-B image |
| **`scripts/make_synthetic_dvr.py`** | Full DVR ring-buffer simulator: H.264/H.265 clips, overwrite, delete, damage, ground_truth.json | **IMPLEMENTED** | `tests/unit/test_synthetic_dvr_pipeline.py` (100%; pure-Python path; ffmpeg path enhanced) |
| **`scripts/validate_recovery.py`** | Precision / recall / byte-rate pipeline validator vs ground truth | **IMPLEMENTED** | `tests/unit/test_synthetic_dvr_pipeline.py` (100%) |
| **`scripts/verify_ledger.py`** | Standalone zero-dependency ledger audit CLI | **IMPLEMENTED** | Audits JSONL custody logs |

---

## Synthetic Validation Results (INFORMATIONAL ONLY — See Warning)

> **⚠ WARNING: All figures below come from SYNTHETIC data generated by `make_synthetic_dvr.py`.**
> They MUST NOT be cited as real-device performance in any submission, paper, or court report.
> See `docs/validation/validation-plan.md` for full methodology and disclaimer.

Run `make validate` (or `python scripts/validate_recovery.py scripts/synthetic_data/synthetic_dvr.img scripts/synthetic_data/ground_truth.json`) to regenerate current results.

| Metric | Value (Synthetic, seed=42, 2ch×4 clips) |
|---|---|
| Recall | ≥ 0 % (non-zero verified by test gate) |
| Precision | Reported in JSON output |
| Byte recovery rate | Reported in JSON output |
| Exact matches | Reported in JSON output |
| Partial matches | Reported in JSON output |

---

## Forensic Integrity Pledge

In adherence to scientific guidelines (SWGDE / ASTM E3016) and legal obligations under Section 63 of Bharatiya Sakshya Adhiniyam, 2023:
- Real vendor specifications are **never fabricated** without hardware lab verification.
- Stubs explicitly raise `NotImplementedError` rather than returning synthetic or misleading results.
- All synthetic validation results embed a machine-readable `"warning"` field in their JSON output.
