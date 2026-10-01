# Standard Operating Procedure (SOP): Forensic Reporting & Section 63 BSA Certification

## 1. Purpose
Define the procedure for generating judicial reports and evidentiary certificates under Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA) / Section 65B of Indian Evidence Act (IEA).

## 2. Mandatory Report Inclusions
1. **Officer Particulars**: Name, designation, police station / agency, credentials.
2. **Device Hardware Information**: Make, model, serial number, physical seizure conditions.
3. **Forensic Hashes**: MD5 and SHA-256 digests computed at intake and matched at export.
4. **Tool Integrity Statement**: Certification that FrameProof operated in an uncorrupted, air-gapped environment.
5. **Timeline Triangulation Details**: RTC offset, OSD OCR cross-reference, and reconciled timestamps.
6. **Cryptographic Proofs**: Merkle root hash of all recovered frames, and the hash of the immutable custody log.

## 3. Section 63 BSA Certificate
- Print or digitally sign the generated certificate.
- Attach cryptographic hash verification summary as an appendix for the presiding judicial magistrate.
