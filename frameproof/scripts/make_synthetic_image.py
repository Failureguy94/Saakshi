#!/usr/bin/env python3
"""FrameProof Synthetic Forensic Disk Image Generator.

Purpose: Generate deterministic synthetic raw disk images injected with known Annex-B NAL units
         (SPS, PPS, IDR, non-IDR, HEVC VPS) at precise offsets to establish ground truth for testing.
Inputs: Target file path, disk size, and layout parameters.
Outputs: Raw disk image file (.raw) and ground-truth metadata structure.
Status: Implemented
"""

import argparse
import json
from pathlib import Path
from typing import Any

# Standard NAL units for ground truth verification
SYNTHETIC_GROUND_TRUTH: list[dict[str, Any]] = [
    {
        "offset": 512,
        "prefix_length": 4,
        "prefix": b"\x00\x00\x00\x01",
        "header_byte": 0x67,  # H.264 SPS (type 7)
        "h264_type": 7,
        "h264_name": "SPS",
        "payload": b"\x67\x42\x00\x1f\x96\x54\x05\x01\xe9\x80",
    },
    {
        "offset": 1024,
        "prefix_length": 4,
        "prefix": b"\x00\x00\x00\x01",
        "header_byte": 0x68,  # H.264 PPS (type 8)
        "h264_type": 8,
        "h264_name": "PPS",
        "payload": b"\x68\xce\x3c\x80",
    },
    {
        "offset": 2048,
        "prefix_length": 3,
        "prefix": b"\x00\x00\x01",
        "header_byte": 0x65,  # H.264 IDR Slice (type 5)
        "h264_type": 5,
        "h264_name": "IDR_SLICE",
        "payload": b"\x65\x88\x84\x00\x10\xff\xee\xdd\xcc\xbb",
    },
    {
        "offset": 4096,
        "prefix_length": 3,
        "prefix": b"\x00\x00\x01",
        "header_byte": 0x41,  # H.264 Non-IDR Slice (type 1)
        "h264_type": 1,
        "h264_name": "NON_IDR_SLICE",
        "payload": b"\x41\x9a\x11\x22\x33\x44\x55",
    },
    {
        "offset": 8192,
        "prefix_length": 4,
        "prefix": b"\x00\x00\x00\x01",
        "header_byte": 0x40,  # H.265 VPS (type 32: (0x40 >> 1) & 0x3F == 32)
        "h264_type": 0,
        "h265_type": 32,
        "h265_name": "VPS",
        "payload": b"\x40\x01\x0c\x01\xff\xff",
    },
]


def generate_synthetic_disk_image(
    output_path: Path | str,
    total_size_bytes: int = 16384,
    ground_truth: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build a deterministic raw disk image with known NAL start codes."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    gt = ground_truth or SYNTHETIC_GROUND_TRUTH

    # Create bytearray populated with pseudo-random deterministic filler
    image_buf = bytearray(total_size_bytes)
    for i in range(total_size_bytes):
        image_buf[i] = (i * 37 + 13) & 0xFF

    # Inject NAL units at designated offsets
    for item in gt:
        offset = item["offset"]
        prefix = item["prefix"]
        payload = item["payload"]
        full_block = prefix + payload

        if offset + len(full_block) > total_size_bytes:
            raise ValueError(f"Offset {offset} + length {len(full_block)} exceeds disk size {total_size_bytes}")

        image_buf[offset : offset + len(full_block)] = full_block

    with open(path, "wb") as f:
        f.write(image_buf)

    return gt


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Generate synthetic disk image with known NAL start codes.")
    parser.add_argument("--output", "-o", default="synthetic_disk.raw", help="Output file path")
    parser.add_argument("--size", "-s", type=int, default=16384, help="Total size in bytes")
    parser.add_argument("--metadata", "-m", default=None, help="Optional output JSON path for ground truth metadata")
    args = parser.parse_args()

    gt = generate_synthetic_disk_image(args.output, total_size_bytes=args.size)
    print(f"Generated synthetic disk image: {args.output} ({args.size} bytes, {len(gt)} injected NAL units)")

    if args.metadata:
        # Strip binary fields for JSON serialization
        clean_gt = [
            {k: v for k, v in item.items() if k not in ("prefix", "payload")}
            for item in gt
        ]
        with open(args.metadata, "w", encoding="utf-8") as f:
            json.dump(clean_gt, f, indent=2)
        print(f"Ground truth metadata saved: {args.metadata}")


if __name__ == "__main__":
    main()
