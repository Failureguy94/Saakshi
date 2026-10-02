"""Tests for nal_carver.py — GOP grouping and SegmentRecord.

These tests complement the existing test_nal_carver.py (start code detection).
They focus on group_into_gops() and SegmentRecord.compute_confidence().

Status: Tests for implemented functionality.
"""

from __future__ import annotations

from app.modules.recovery.nal_carver import (
    SegmentRecord,
    default_nal_carver,
    group_into_gops,
)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers to build minimal Annex-B test streams
# ──────────────────────────────────────────────────────────────────────────────

def _nal(header_byte: int, payload: bytes = b"\x00" * 16) -> bytes:
    return b"\x00\x00\x00\x01" + bytes([header_byte]) + payload


def _h264_gop(with_sps: bool = True, with_pps: bool = True, idr_size: int = 64) -> bytes:
    parts = []
    if with_sps:
        parts.append(_nal(0x67))     # SPS
    if with_pps:
        parts.append(_nal(0x68))     # PPS
    parts.append(_nal(0x65, b"\x00" * idr_size))  # IDR
    parts.append(_nal(0x61))         # P-frame (NON_IDR)
    return b"".join(parts)


def _h265_gop(with_vps: bool = True, with_sps: bool = True, with_pps: bool = True) -> bytes:
    parts = []
    if with_vps:
        parts.append(_nal(0x40))  # VPS (h265_type = 32)
    if with_sps:
        parts.append(_nal(0x42))  # SPS (h265_type = 33)
    if with_pps:
        parts.append(_nal(0x44))  # PPS (h265_type = 34)
    parts.append(_nal(0x26))      # IDR_W_RADL (h265_type = 19)
    parts.append(_nal(0x02))      # TRAIL_R
    return b"".join(parts)


class TestSegmentRecordConfidence:
    def test_full_gop_confidence_is_1(self) -> None:
        seg = SegmentRecord(
            offset=0, length=100, codec="h264", gop_index=0,
            has_sps=True, has_pps=True, has_idr=True, nal_count=4,
        )
        seg.compute_confidence()
        assert seg.confidence == 1.0

    def test_no_idr_low_confidence(self) -> None:
        seg = SegmentRecord(
            offset=0, length=100, codec="h264", gop_index=0,
            has_sps=True, has_pps=True, has_idr=False, nal_count=3,
        )
        seg.compute_confidence()
        assert seg.confidence <= 0.6

    def test_only_idr_medium_confidence(self) -> None:
        seg = SegmentRecord(
            offset=0, length=100, codec="h264", gop_index=0,
            has_sps=False, has_pps=False, has_idr=True, nal_count=1,
        )
        seg.compute_confidence()
        assert 0.3 < seg.confidence < 0.6

    def test_empty_segment_zero_confidence(self) -> None:
        seg = SegmentRecord(offset=0, length=0, codec="unknown", gop_index=0)
        seg.compute_confidence()
        assert seg.confidence == 0.0


class TestGroupIntoGops:
    def test_single_h264_gop(self) -> None:
        data = _h264_gop()
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)
        assert len(segs) >= 1
        first = segs[0]
        assert first.has_idr
        assert first.has_sps
        assert first.has_pps
        assert first.codec == "h264"
        assert first.confidence == 1.0

    def test_two_h264_gops(self) -> None:
        data = _h264_gop() + _h264_gop()
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)
        assert len(segs) == 2
        for seg in segs:
            assert seg.has_idr
            assert seg.codec == "h264"

    def test_h265_gop_detected(self) -> None:
        data = _h265_gop()
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)
        assert len(segs) >= 1
        assert segs[0].codec == "h265"
        assert segs[0].has_idr
        assert segs[0].has_sps

    def test_missing_sps_lowers_confidence(self) -> None:
        data = _h264_gop(with_sps=False)
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)
        assert len(segs) >= 1
        # Without SPS the confidence must be < 1.0
        assert segs[0].confidence < 1.0

    def test_empty_nal_list_returns_empty(self) -> None:
        segs = group_into_gops([])
        assert segs == []

    def test_gop_offsets_are_within_data(self) -> None:
        data = _h264_gop() * 3
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)
        for seg in segs:
            assert seg.offset >= 0
            assert seg.offset + seg.length <= len(data) + 1  # +1 tolerance for last NAL estimate

    def test_mixed_codec_stream_groups_independently(self) -> None:
        data = _h264_gop() + _h265_gop()
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)
        # Should find segments of at least 2 different GOPs
        assert len(segs) >= 2


class TestNALUnitPredicates:
    def test_h264_idr_predicate(self) -> None:
        data = _nal(0x65)  # IDR header byte
        nals = default_nal_carver.carve_bytes(data)
        assert len(nals) == 1
        assert nals[0].is_h264_idr()
        assert nals[0].is_h264_param_set() is False

    def test_h264_sps_predicate(self) -> None:
        data = _nal(0x67)  # SPS
        nals = default_nal_carver.carve_bytes(data)
        assert nals[0].is_h264_param_set()
        assert nals[0].is_h264_idr() is False

    def test_h265_irap_predicate(self) -> None:
        data = _nal(0x26)  # IDR_W_RADL: header = (19<<1) = 38 = 0x26
        nals = default_nal_carver.carve_bytes(data)
        assert nals[0].is_h265_irap()

    def test_h265_vps_is_param_set(self) -> None:
        data = _nal(0x40)  # VPS: header = (32<<1) = 64 = 0x40
        nals = default_nal_carver.carve_bytes(data)
        assert nals[0].is_h265_param_set()
