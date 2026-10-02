#!/usr/bin/env python3
"""Saakshi Synthetic DVR Disk Image Generator.

Purpose:
    Generate a deterministic raw disk image that mimics a DVR ring-buffer recording
    with a custom index table, H.264 / H.265 Annex-B NAL payload, simulated overwrites,
    deleted index entries, and corrupt GOP headers.  Emits a ground_truth.json so the
    validate_recovery script can measure precision and recall objectively.

    When ffmpeg is present it is used to encode short clips with burned-in OSD
    timestamps (realistic codec data).  When ffmpeg is absent the script falls back
    to a pure-Python minimal Annex-B bitstream that still exercises the carver.

Inputs:
    CLI arguments (see --help).

Outputs:
    <out-dir>/synthetic_dvr.img      – raw disk image (read-only after creation)
    <out-dir>/ground_truth.json      – clip layout, true timestamps, damage flags

Status: Implemented (pure-Python fallback; ffmpeg path enhanced).

WARNING: Output images contain SYNTHETIC data only.  Never use real surveillance
footage as input.  Results from synthetic validation MUST NOT be presented as
real-device performance.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import shutil
import struct
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("make_synthetic_dvr")

# ──────────────────────────────────────────────────────────────────────────────
# Disk layout constants
# ──────────────────────────────────────────────────────────────────────────────
SECTOR_SIZE = 512          # bytes per sector
INDEX_SECTORS = 16         # sectors reserved for the index table at disk start
INDEX_ENTRY_SIZE = 64      # bytes per index entry (fixed)
MAX_INDEX_ENTRIES = (INDEX_SECTORS * SECTOR_SIZE) // INDEX_ENTRY_SIZE  # 128
CODEC_H264 = 0x01
CODEC_H265 = 0x02

# Index entry binary layout (little-endian, total 64 bytes):
#   magic       4s    b"SIDX"        4
#   version     B     1              1
#   channel     B     0-3            1
#   codec       B     CODEC_*        1
#   flags       B     bitmask        1
#   start_lba   I     LBA            4
#   block_count I     sectors        4
#   byte_length I     payload bytes  4
#   ts_start    Q     unix epoch     8
#   ts_end      Q     unix epoch     8
#                                  ---
#   subtotal                        36
#   reserved    28s   zero-padded   28
#                                  ---
#   total                           64
INDEX_STRUCT = struct.Struct("<4sBBBBIIIQQ28s")
assert INDEX_STRUCT.size == INDEX_ENTRY_SIZE, f"Expected 64, got {INDEX_STRUCT.size}"


@dataclass
class ClipRecord:
    """Ground-truth record for one video clip written to the synthetic disk."""

    clip_id: int
    channel: int
    codec: str               # "h264" or "h265"
    start_lba: int           # relative to data area
    block_count: int
    byte_length: int
    ts_start: int            # unix epoch seconds
    ts_end: int
    deleted: bool = False    # index entry was zeroed
    overwritten: bool = False  # data partially overwritten by later clip
    damaged: bool = False    # a GOP header byte was zeroed


def _build_minimal_annexb_clip(
    channel: int,
    codec_id: int,
    duration_secs: int,
    fps: int,
    seed: int,
) -> bytes:
    """Pure-Python fallback: build a minimal valid Annex-B bitstream.

    Generates:
        H.264: SPS + PPS + (IDR + N×P-frame) per second
        H.265: VPS + SPS + PPS + (IDR + N×P-frame) per second

    The SPS/PPS contain real enough header bytes to be classified correctly
    by the NAL carver.  The slice payloads are random noise — not decodable
    by a real decoder but structurally valid for carving purposes.

    Args:
        channel:      0-3 simulated channel index (used in seed mixing)
        codec_id:     CODEC_H264 or CODEC_H265
        duration_secs: clip duration in seconds
        fps:          frames per second
        seed:         deterministic seed

    Returns:
        Raw Annex-B byte string.
    """
    rng = random.Random(seed ^ (channel << 24))

    def nal(header_byte: int, payload_size: int = 128) -> bytes:
        start_code = b"\x00\x00\x00\x01"
        payload = bytes([rng.randint(0, 255) for _ in range(payload_size)])
        return start_code + bytes([header_byte]) + payload

    frames: list[bytes] = []

    if codec_id == CODEC_H264:
        # SPS = NAL type 7 (header byte = 0x67), PPS = type 8 (0x68)
        gop_header = nal(0x67, 32) + nal(0x68, 8)
        for sec in range(duration_secs):
            frames.append(gop_header)
            # IDR = type 5 (header byte = 0x65)
            frames.append(nal(0x65, 512))
            for _ in range(fps - 1):
                # P-frame = type 1 (header byte = 0x61)
                frames.append(nal(0x61, 256))
    else:
        # H.265: VPS=32 (0x40), SPS=33 (0x42), PPS=34 (0x44)
        # IRAP/IDR_W_RADL=19 → header byte = (19 << 1) = 0x26
        gop_header = nal(0x40, 24) + nal(0x42, 24) + nal(0x44, 8)
        for sec in range(duration_secs):
            frames.append(gop_header)
            frames.append(nal(0x26, 512))   # IDR_W_RADL
            for _ in range(fps - 1):
                frames.append(nal(0x02, 256))   # TRAIL_R

    return b"".join(frames)


def _encode_with_ffmpeg(
    channel: int,
    codec: str,
    duration_secs: int,
    ts_start: int,
    out_path: Path,
    seed: int,
) -> bool:
    """Attempt to encode a clip using ffmpeg with burned-in OSD timestamp.

    Returns True on success, False if ffmpeg unavailable or fails.
    """
    if not shutil.which("ffmpeg"):
        return False

    import datetime

    dt = datetime.datetime.utcfromtimestamp(ts_start).strftime("%Y-%m-%d %H:%M:%S")
    label = f"CH{channel:02d} | {dt} | SYNTHETIC"
    vcodec = "libx264" if codec == "h264" else "libx265"
    pix_fmt = "yuv420p"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x1a1a2e:size=320x240:rate=15:duration={duration_secs}",
        "-vf", f"drawtext=text='{label}':fontsize=14:fontcolor=white:x=4:y=4",
        "-c:v", vcodec,
        "-preset", "ultrafast",
        "-pix_fmt", pix_fmt,
        "-g", "15",
        "-bsf:v", "h264_mp4toannexb" if codec == "h264" else "hevc_mp4toannexb",
        "-f", "rawvideo" if codec == "h264" else "hevc",
        str(out_path),
    ]
    # Use h264 raw stream format
    if codec == "h264":
        cmd[-2] = "h264"
    else:
        cmd[-2] = "hevc"

    result = subprocess.run(cmd, capture_output=True, timeout=60)
    if result.returncode != 0:
        log.warning("ffmpeg failed for channel %d: %s", channel, result.stderr[-200:])
        return False
    return True


def _align_up(n: int, align: int) -> int:
    return ((n + align - 1) // align) * align


def build_synthetic_dvr(
    num_channels: int,
    clips_per_channel: int,
    clip_duration: int,
    fps: int,
    overwrite_factor: float,
    delete_fraction: float,
    damage_fraction: float,
    use_h265: bool,
    ts_base: int,
    seed: int,
    out_dir: Path,
) -> tuple[Path, Path]:
    """Build the synthetic disk image and ground_truth.json.

    Args:
        num_channels:     2–4 camera channels.
        clips_per_channel: number of clips per channel.
        clip_duration:    seconds per clip.
        fps:              frames per second (used only in pure-Python path).
        overwrite_factor: fraction 0.0–1.0; a ring-buffer overwrite of this
                          fraction of the oldest clips' data sectors.
        delete_fraction:  fraction of index entries to zero-out (simulate deletion).
        damage_fraction:  fraction of clips whose first GOP header byte is zeroed.
        use_h265:         if True, alternate channels use H.265.
        ts_base:          unix epoch seconds for the first clip's start timestamp.
        seed:             deterministic seed.
        out_dir:          output directory (created if absent).

    Returns:
        Tuple of (image_path, ground_truth_path).
    """
    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    img_path = out_dir / "synthetic_dvr.img"
    gt_path = out_dir / "ground_truth.json"

    # ── Build clip payloads ──────────────────────────────────────────────────
    all_clips: list[tuple[ClipRecord, bytes]] = []
    ts_cursor = ts_base

    for ch in range(num_channels):
        codec_id = CODEC_H265 if (use_h265 and ch % 2 == 1) else CODEC_H264
        codec_str = "h265" if codec_id == CODEC_H265 else "h264"

        for clip_idx in range(clips_per_channel):
            clip_seed = seed ^ (ch << 16) ^ clip_idx
            ts_start = ts_cursor
            ts_end = ts_start + clip_duration
            ts_cursor += clip_duration + rng.randint(0, 2)

            # Try ffmpeg first, fall back to pure-Python
            payload: Optional[bytes] = None
            with tempfile.NamedTemporaryFile(suffix=f".{codec_str}", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            try:
                if _encode_with_ffmpeg(ch, codec_str, clip_duration, ts_start, tmp_path, clip_seed):
                    payload = tmp_path.read_bytes()
            finally:
                tmp_path.unlink(missing_ok=True)

            if not payload:
                payload = _build_minimal_annexb_clip(
                    channel=ch,
                    codec_id=codec_id,
                    duration_secs=clip_duration,
                    fps=fps,
                    seed=clip_seed,
                )

            # Pad to sector boundary
            pad = _align_up(len(payload), SECTOR_SIZE) - len(payload)
            payload = payload + (b"\x00" * pad)
            block_count = len(payload) // SECTOR_SIZE

            rec = ClipRecord(
                clip_id=len(all_clips),
                channel=ch,
                codec=codec_str,
                start_lba=0,          # assigned below
                block_count=block_count,
                byte_length=len(payload) - pad,
                ts_start=ts_start,
                ts_end=ts_end,
            )
            all_clips.append((rec, payload))

    # ── Assign LBAs (sequential layout) ─────────────────────────────────────
    current_lba = 0
    for rec, payload in all_clips:
        rec.start_lba = current_lba
        current_lba += rec.block_count

    total_data_sectors = current_lba
    total_sectors = INDEX_SECTORS + total_data_sectors
    disk_size = total_sectors * SECTOR_SIZE

    # ── Apply ring-buffer overwrite ──────────────────────────────────────────
    num_to_overwrite = int(len(all_clips) * overwrite_factor)
    overwrite_targets: set[int] = set(
        rng.sample(range(len(all_clips)), min(num_to_overwrite, len(all_clips)))
    )
    for idx in overwrite_targets:
        all_clips[idx][0].overwritten = True
        # Zero out first half of the data
        half = len(all_clips[idx][1]) // 2
        all_clips[idx] = (all_clips[idx][0], (b"\x00" * half) + all_clips[idx][1][half:])

    # ── Apply damage (corrupt first GOP header byte) ─────────────────────────
    num_to_damage = int(len(all_clips) * damage_fraction)
    damage_targets: set[int] = set(
        rng.sample(
            [i for i in range(len(all_clips)) if i not in overwrite_targets],
            min(num_to_damage, len(all_clips) - len(overwrite_targets)),
        )
    )
    for idx in damage_targets:
        rec, payload = all_clips[idx]
        rec.damaged = True
        # Find first 00 00 00 01 (IDR) and zero header byte
        pos = payload.find(b"\x00\x00\x00\x01")
        if pos >= 0 and pos + 5 < len(payload):
            ba = bytearray(payload)
            ba[pos + 4] = 0x00          # corrupt the NAL header byte
            payload = bytes(ba)
        all_clips[idx] = (rec, payload)

    # ── Apply deletions (zero index entries) ─────────────────────────────────
    num_to_delete = int(len(all_clips) * delete_fraction)
    delete_targets: set[int] = set(
        rng.sample(range(len(all_clips)), min(num_to_delete, len(all_clips)))
    )
    for idx in delete_targets:
        all_clips[idx][0].deleted = True

    # ── Write disk image ─────────────────────────────────────────────────────
    disk = bytearray(disk_size)

    # Write index table
    for entry_idx, (rec, _) in enumerate(all_clips):
        if entry_idx >= MAX_INDEX_ENTRIES:
            log.warning("Too many clips (%d); index table truncated at %d", len(all_clips), MAX_INDEX_ENTRIES)
            break
        flags = 0
        if rec.deleted:
            flags |= 0x01
        if rec.damaged:
            flags |= 0x02
        if rec.overwritten:
            flags |= 0x04
        entry = INDEX_STRUCT.pack(
            b"SIDX",
            1,              # version
            rec.channel,
            CODEC_H264 if rec.codec == "h264" else CODEC_H265,
            flags,
            rec.start_lba,
            rec.block_count,
            rec.byte_length,
            rec.ts_start,
            rec.ts_end,
            b"\x00" * 28,  # reserved
        )
        if rec.deleted:
            entry = b"\x00" * INDEX_ENTRY_SIZE   # wipe the index entry
        offset = entry_idx * INDEX_ENTRY_SIZE
        disk[offset : offset + INDEX_ENTRY_SIZE] = entry

    # Write clip payloads into data area
    for rec, payload in all_clips:
        data_offset = (INDEX_SECTORS + rec.start_lba) * SECTOR_SIZE
        disk[data_offset : data_offset + len(payload)] = payload

    img_path.write_bytes(bytes(disk))
    # Make the image read-only to enforce forensic discipline
    img_path.chmod(0o444)
    log.info("Wrote disk image: %s (%d bytes)", img_path, len(disk))

    # ── Write ground truth ───────────────────────────────────────────────────
    gt: dict[str, object] = {
        "generator": "make_synthetic_dvr.py",
        "seed": seed,
        "disk_image": str(img_path),
        "sector_size": SECTOR_SIZE,
        "index_sectors": INDEX_SECTORS,
        "index_entry_size": INDEX_ENTRY_SIZE,
        "data_area_start_byte": INDEX_SECTORS * SECTOR_SIZE,
        "total_bytes": disk_size,
        "clips": [
            {
                **asdict(rec),
                # absolute byte offsets in the disk image
                "abs_start_byte": (INDEX_SECTORS + rec.start_lba) * SECTOR_SIZE,
                "abs_end_byte": (INDEX_SECTORS + rec.start_lba + rec.block_count) * SECTOR_SIZE,
            }
            for rec, _ in all_clips
        ],
    }
    gt_path.write_text(json.dumps(gt, indent=2))
    log.info("Wrote ground truth: %s (%d clips)", gt_path, len(all_clips))
    return img_path, gt_path


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a synthetic DVR disk image with ground truth for Saakshi recovery tests."
    )
    parser.add_argument("--channels", type=int, default=2, choices=[2, 3, 4], help="Number of camera channels")
    parser.add_argument("--clips-per-channel", type=int, default=4, help="Clips per channel")
    parser.add_argument("--clip-duration", type=int, default=5, help="Clip duration in seconds")
    parser.add_argument("--fps", type=int, default=15, help="Frames per second (pure-Python path only)")
    parser.add_argument("--overwrite-factor", type=float, default=0.2, help="Fraction of clips to partially overwrite")
    parser.add_argument("--delete-fraction", type=float, default=0.25, help="Fraction of index entries to delete")
    parser.add_argument("--damage-fraction", type=float, default=0.15, help="Fraction of clips to damage (corrupt GOP header)")
    parser.add_argument("--h265", action="store_true", help="Alternate odd channels to H.265")
    parser.add_argument("--ts-base", type=int, default=1_700_000_000, help="Unix timestamp for first clip")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic seed")
    parser.add_argument("--out-dir", type=Path, default=Path("scripts/synthetic_data"), help="Output directory")
    args = parser.parse_args()

    img_path, gt_path = build_synthetic_dvr(
        num_channels=args.channels,
        clips_per_channel=args.clips_per_channel,
        clip_duration=args.clip_duration,
        fps=args.fps,
        overwrite_factor=args.overwrite_factor,
        delete_fraction=args.delete_fraction,
        damage_fraction=args.damage_fraction,
        use_h265=args.h265,
        ts_base=args.ts_base,
        seed=args.seed,
        out_dir=args.out_dir,
    )
    print(f"Image : {img_path}")
    print(f"Ground truth: {gt_path}")


if __name__ == "__main__":
    main()
