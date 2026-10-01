# Standard Operating Procedure (SOP): Video Stream Recovery & Carving

## 1. Purpose
Define the process for recovering fragmented, deleted, ring-buffer overwritten, or unindexed video footage from DVR/NVR raw disk images.

## 2. Ingestion Principle
- **Strict Read-Only Execution**: Carving and recovery routines never write to or modify the source disk image.
- Working scratch spaces, carved NAL streams, and reassembled video files are strictly written to isolated case storage directories.

## 3. Operational Workflow
1. **OEM Identification**:
   - Run Saakshi signature scanner across volume superblocks and partition tables.
   - If an OEM profile matches (e.g. DHFS, HIKFS), execute the index-guided parser.
2. **Orphan & Unallocated Slack Carving**:
   - Scan unallocated sectors for H.264 / H.265 Annex-B start codes (`0x000001` / `0x00000001`).
   - Extract NAL units (SPS, PPS, IDR slices).
3. **Ring Buffer Overwrite Analysis**:
   - Analyze sector sequence stamps to detect where circular FIFO recording looped back.
   - Separate active recordings from residual previous cycle fragments.
4. **GOP Reassembly**:
   - Synthesize missing SPS/PPS parameter sets where lost.
   - Validate decoding timestamps to ensure monotonic playback.
5. **Ledger Record**:
   - Calculate Merkle root of carved segments.
   - Append Carve Completed entry to the chain of custody log.
