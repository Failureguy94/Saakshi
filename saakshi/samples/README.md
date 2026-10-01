# Evidence Samples Directory & Lab Image Guidelines

> **CRITICAL FORENSIC MANDATE**:
> **NEVER COMMIT REAL SURVEILLANCE FOOTAGE, SEIZED DISK IMAGES, OR ACTUAL EVIDENCE TO THIS REPOSITORY OR ANY VERSION CONTROL SYSTEM.**
> Violating this compromises chain of custody, breaches judicial privacy statutes, and incurs severe legal liabilities under the Bharatiya Sakshya Adhiniyam, 2023 and IT Act, 2000.

---

## 1. Allowed Artifacts in Repository
- Synthetic disk images generated deterministically via `scripts/make_synthetic_image.py`.
- Unit test fixtures containing simulated NAL unit headers and pseudo-random filler.

---

## 2. Setting Up Local Lab Test Images
To test with physical lab DVR images (non-case test media acquired in a forensics lab):

1. Connect your write-blocked target storage drive.
2. Place raw disk images (`.raw`, `.dd`, `.img`) or EnCase images (`.E01`) inside an uncommitted local directory:
   ```bash
   mkdir -p samples/lab_drives/
   ```
3. Verify that `samples/*.raw`, `samples/*.dd`, `samples/*.img`, and `samples/*.E01` are ignored by git:
   ```bash
   git status --ignored
   ```
4. Record reference hashes before executing analysis:
   ```bash
   sha256sum samples/lab_drives/test_hikvision.raw > samples/lab_drives/test_hikvision.raw.sha256
   ```
