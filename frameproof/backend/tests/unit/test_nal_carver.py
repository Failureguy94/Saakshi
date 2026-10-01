"""Unit tests for Annex-B NAL carver against synthetic ground truth."""

import sys
import tempfile
from pathlib import Path

from app.modules.recovery.nal_carver import PythonAnnexBCarver

# Import synthetic generator from scripts
SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
from make_synthetic_image import (  # type: ignore # noqa: E402
    SYNTHETIC_GROUND_TRUTH,
    generate_synthetic_disk_image,
)


def test_nal_carver_against_synthetic_ground_truth() -> None:
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        gt = generate_synthetic_disk_image(tmp_path, total_size_bytes=16384)
        carver = PythonAnnexBCarver()

        with open(tmp_path, "rb") as f:
            raw_bytes = f.read()

        carved = carver.carve_bytes(raw_bytes)

        # Match each ground truth entry
        for expected in gt:
            matched = [c for c in carved if c.start_offset == expected["offset"]]
            assert len(matched) == 1, f"Failed to carve NAL at offset {expected['offset']}"
            unit = matched[0]

            assert unit.prefix_length == expected["prefix_length"]
            assert unit.header_byte == expected["header_byte"]

            if "h264_name" in expected:
                assert unit.h264_name == expected["h264_name"]
            if "h265_name" in expected:
                assert unit.h265_name == expected["h265_name"]

    finally:
        tmp_path.unlink()


def test_nal_carver_streaming_chunk_boundaries() -> None:
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        generate_synthetic_disk_image(tmp_path, total_size_bytes=16384)
        carver = PythonAnnexBCarver()

        # Read with small chunk size (e.g. 512 bytes) to force chunks spanning start codes
        stream_results = []
        with open(tmp_path, "rb") as f:
            for unit in carver.carve_stream(f, chunk_size=512):
                stream_results.append(unit)

        offsets = {u.start_offset for u in stream_results}
        for expected in SYNTHETIC_GROUND_TRUTH:
            assert expected["offset"] in offsets, f"Streaming carver missed offset {expected['offset']}"

    finally:
        tmp_path.unlink()
