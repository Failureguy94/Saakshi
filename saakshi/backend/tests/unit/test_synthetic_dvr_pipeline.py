"""Tests for the full synthetic DVR pipeline: generate → carve → repair → validate.

These tests exercise make_synthetic_dvr.build_synthetic_dvr() and
validate_recovery.run_validation() together using only in-process function
calls (no subprocess, no ffmpeg).

Status: Tests for implemented functionality (pure-Python path only).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Allow importing scripts without installing them as packages
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from make_synthetic_dvr import build_synthetic_dvr  # type: ignore[import-not-found]  # noqa: E402
from validate_recovery import (  # type: ignore[import-not-found]  # noqa: E402
    _byte_recovery_rate,
    _match_clips_to_segments,
)


@pytest.fixture(scope="module")
def synthetic_dvr(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path, dict]:  # type: ignore[type-arg]
    """Build a small synthetic DVR image for pipeline tests."""
    out = tmp_path_factory.mktemp("dvr")
    img, gt = build_synthetic_dvr(
        num_channels=2,
        clips_per_channel=3,
        clip_duration=3,
        fps=10,
        overwrite_factor=0.1,
        delete_fraction=0.15,
        damage_fraction=0.1,
        use_h265=False,
        ts_base=1_700_000_000,
        seed=99,
        out_dir=out,
    )
    gt_data = json.loads(gt.read_text())
    return img, gt, gt_data


class TestSyntheticDvrGenerator:
    def test_image_created(self, synthetic_dvr: tuple[Path, Path, dict]) -> None:  # type: ignore[type-arg]
        img, gt, gt_data = synthetic_dvr
        assert img.exists()
        assert img.stat().st_size > 0

    def test_ground_truth_created(self, synthetic_dvr: tuple[Path, Path, dict]) -> None:  # type: ignore[type-arg]
        img, gt, gt_data = synthetic_dvr
        assert gt.exists()
        assert "clips" in gt_data

    def test_clip_count(self, synthetic_dvr: tuple[Path, Path, dict]) -> None:  # type: ignore[type-arg]
        img, gt, gt_data = synthetic_dvr
        # 2 channels × 3 clips = 6 clips
        assert len(gt_data["clips"]) == 6

    def test_clips_have_valid_offsets(self, synthetic_dvr: tuple[Path, Path, dict]) -> None:  # type: ignore[type-arg]
        img, gt, gt_data = synthetic_dvr
        img_size = img.stat().st_size
        for clip in gt_data["clips"]:
            assert clip["abs_start_byte"] >= 0
            assert clip["abs_end_byte"] <= img_size
            assert clip["abs_start_byte"] < clip["abs_end_byte"]

    def test_ground_truth_has_damage_flags(self, synthetic_dvr: tuple[Path, Path, dict]) -> None:  # type: ignore[type-arg]
        img, gt, gt_data = synthetic_dvr
        # At least some clips should have boolean fields
        for clip in gt_data["clips"]:
            assert "deleted" in clip
            assert "damaged" in clip
            assert "overwritten" in clip

    def test_disk_image_is_read_only(self, synthetic_dvr: tuple[Path, Path, dict]) -> None:  # type: ignore[type-arg]
        img, gt, gt_data = synthetic_dvr
        mode = img.stat().st_mode
        # Owner write bit (0o200) should be unset
        assert not (mode & 0o200), "disk image should be read-only after creation"

    def test_deterministic_output(self, tmp_path: Path) -> None:
        """Same seed produces identical images."""
        img1, gt1 = build_synthetic_dvr(
            num_channels=2, clips_per_channel=2, clip_duration=2,
            fps=10, overwrite_factor=0.0, delete_fraction=0.0,
            damage_fraction=0.0, use_h265=False, ts_base=0, seed=7,
            out_dir=tmp_path / "run1",
        )
        img2, gt2 = build_synthetic_dvr(
            num_channels=2, clips_per_channel=2, clip_duration=2,
            fps=10, overwrite_factor=0.0, delete_fraction=0.0,
            damage_fraction=0.0, use_h265=False, ts_base=0, seed=7,
            out_dir=tmp_path / "run2",
        )
        assert img1.read_bytes() == img2.read_bytes()


class TestMatchingLogic:
    """Unit tests for the byte overlap matching logic in validate_recovery."""

    def _make_clip(
        self,
        clip_id: int,
        start: int,
        end: int,
        deleted: bool = False,
        overwritten: bool = False,
    ) -> dict:  # type: ignore[type-arg]
        return {
            "clip_id": clip_id,
            "abs_start_byte": start,
            "abs_end_byte": end,
            "byte_length": end - start,
            "deleted": deleted,
            "overwritten": overwritten,
        }

    def _make_seg(self, offset: int, length: int) -> dict:  # type: ignore[type-arg]
        return {"offset": offset, "length": length, "confidence": 1.0}

    def test_exact_match(self) -> None:
        clips = [self._make_clip(0, 0, 1000)]
        segs = [self._make_seg(0, 1000)]
        result = _match_clips_to_segments(clips, segs)
        assert 0 in result["exact"]
        assert result["missed"] == []

    def test_partial_match_two_segments(self) -> None:
        # Two segments together cover 70% of the clip
        clips = [self._make_clip(0, 0, 1000)]
        segs = [self._make_seg(0, 400), self._make_seg(400, 300)]  # 700/1000 = 70%
        result = _match_clips_to_segments(clips, segs)
        assert 0 in result["partial"] or 0 in result["exact"]

    def test_missed_clip(self) -> None:
        clips = [self._make_clip(0, 0, 1000)]
        segs = [self._make_seg(900, 50)]   # only 5% overlap
        result = _match_clips_to_segments(clips, segs)
        assert 0 in result["missed"]

    def test_false_positive_segment(self) -> None:
        clips = [self._make_clip(0, 0, 100)]
        segs = [
            self._make_seg(0, 100),      # matched
            self._make_seg(50000, 500),  # entirely outside clip → FP
        ]
        result = _match_clips_to_segments(clips, segs)
        assert 1 in result["false_positives"]

    def test_overwritten_clips_excluded(self) -> None:
        clips = [
            self._make_clip(0, 0, 500, overwritten=True),
            self._make_clip(1, 500, 1000),
        ]
        segs = [self._make_seg(500, 500)]
        result = _match_clips_to_segments(clips, segs)
        # Clip 0 (overwritten) must not appear in any result list
        assert 0 not in result["exact"]
        assert 0 not in result["partial"]
        assert 0 not in result["missed"]
        assert result["evaluable_count"] == 1


class TestByteRecoveryRate:
    def _make_clip(self, clip_id: int, start: int, end: int) -> dict:  # type: ignore[type-arg]
        return {"clip_id": clip_id, "abs_start_byte": start, "abs_end_byte": end, "byte_length": end - start, "overwritten": False}

    def _make_seg(self, offset: int, length: int) -> dict:  # type: ignore[type-arg]
        return {"offset": offset, "length": length}

    def test_full_coverage_is_1(self) -> None:
        clips = [self._make_clip(0, 0, 100)]
        segs = [self._make_seg(0, 100)]
        assert _byte_recovery_rate(clips, segs) == 1.0

    def test_no_coverage_is_0(self) -> None:
        clips = [self._make_clip(0, 0, 100)]
        segs = [self._make_seg(200, 100)]   # no overlap
        assert _byte_recovery_rate(clips, segs) == 0.0

    def test_partial_coverage(self) -> None:
        clips = [self._make_clip(0, 0, 100)]
        segs = [self._make_seg(0, 50)]    # covers first half
        rate = _byte_recovery_rate(clips, segs)
        assert 0.49 < rate < 0.51

    def test_empty_clips_returns_1(self) -> None:
        assert _byte_recovery_rate([], []) == 1.0


class TestFullPipeline:
    """Integration test: generate → NAL carve → GOP group → validate metrics."""

    def test_pipeline_produces_nonzero_recall(
        self, synthetic_dvr: tuple[Path, Path, dict], tmp_path: Path  # type: ignore[type-arg]
    ) -> None:
        from io import BytesIO

        from validate_recovery import _match_clips_to_segments  # type: ignore[import-not-found]

        from app.modules.recovery.gop_repair import repair_gops
        from app.modules.recovery.nal_carver import default_nal_carver, group_into_gops

        img, gt, gt_data = synthetic_dvr
        source = img.read_bytes()
        nals = list(default_nal_carver.carve_stream(BytesIO(source)))
        segs = group_into_gops(nals, stream_data=source)
        repaired = repair_gops(segs, source=source).segments

        recovered = [{"offset": s.offset, "length": s.length, "confidence": s.confidence} for s in repaired]
        result = _match_clips_to_segments(gt_data["clips"], recovered)

        total_recovered = len(result["exact"]) + len(result["partial"])
        recall = total_recovered / result["evaluable_count"] if result["evaluable_count"] > 0 else 0.0
        # The pure-Python Annex-B generator writes valid start codes,
        # so the carver should recover at least some of them
        assert recall > 0.0, f"Expected non-zero recall; got {recall}"
