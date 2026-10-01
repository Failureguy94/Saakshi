# Standard Operating Procedure (SOP): Digital Evidence Acquisition

## 1. Purpose
Define the standard operational workflow for forensic image acquisition from surveillance DVR/NVR physical hard drives, SSDs, and SD cards in compliance with forensic chain of custody standards.

## 2. Scope
Applies to all physical media seizures under Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA) and ISO/IEC 27037 standards.

## 3. Mandatory Hardware & Tooling
- Hardware Write-Blocker (Tableau, CRU WiebeTech, or verified hardware SATA/NVMe blocker).
- Forensic Workstation running Saakshi in offline air-gapped mode.
- Sanitized, forensically clean target storage drive.

## 4. Execution Steps
1. **Physical Inspection**: Document physical make, model, serial number, and tamper seals.
2. **Write-Blocker Verification**: Confirm hardware write-blocker LED indicates active write-blocking status.
3. **Mounting**: Ensure disk is attached read-only (`blockdev --setro /dev/sdX`).
4. **Intake Hashing**:
   - Execute Saakshi dual-streaming imager computing MD5 and SHA-256 simultaneously in one pass.
   - Record exact total byte count.
5. **Chain of Custody Logging**:
   - Log the acquisition event to the Saakshi hash-chained custody ledger.
   - Securely store the primary forensic image (`.raw` or `.E01`) in the read-only evidence vault.
