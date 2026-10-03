# Saakshi Forensic Platform
A vendor-agnostic DVR/NVR forensic platform.

**⚠️ Note: All results and models shown here are generated from synthetic data.**

## What is implemented
- **Identification:** Profile matching (VendorX + placeholders)
- **Acquisition:** File hash generation (MD5/SHA256)
- **Parsing:** Extracting indexed segments from a synthetic VendorX index
- **Recovery:** Extracting indexed segments and naive NAL-based carving for deleted H.264 streams
- **Timeline:** Estimating DVR offset (Mock implementation)
- **Analytics:** Basic frame-difference motion detection using OpenCV
- **Custody:** Append-only hash chain and Merkle tree stored in SQLite
- **Reporting:** PDF generation via ReportLab with BSA 2023 compliance section
- **UI:** Streamlit dashboard

## What is planned
- True binary parsing of diverse real-world proprietary formats
- Advanced carving algorithms
- Full timeline PTS sync and OCR extraction
- Object detection in analytics

## Run Instructions
```bash
make init
make demo
make ui
```
