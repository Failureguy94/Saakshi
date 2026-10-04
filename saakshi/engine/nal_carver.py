"""Saakshi Annex-B NAL Carver (H.264 / H.265).

Purpose:
    Scan raw binary streams or disk images for Annex-B start codes
    (00 00 01 / 00 00 00 01), extract NAL unit headers, classify NAL types
    across H.264 (AVC) and H.265 (HEVC), and group consecutive NAL units
    into GOP-level SegmentRecords with offset, length, codec guess, and a
    confidence score.

Inputs:  Binary streams or raw byte sequences.
Outputs: NALUnit list / generator; SegmentRecord list from group_into_gops().
Status:  Implemented (Python backend; interface designed for Rust acceleration).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass, field
from io import BufferedReader
from typing import BinaryIO, NamedTuple

# ──────────────────────────────────────────────────────────────────────────────
# NAL type tables
# ──────────────────────────────────────────────────────────────────────────────

H264_NAL_NAMES: dict[int, str] = {
    1: "NON_IDR_SLICE",
    2: "SLICE_DATA_PART_A",
    3: "SLICE_DATA_PART_B",
    4: "SLICE_DATA_PART_C",
    5: "IDR_SLICE",
    6: "SEI",
    7: "SPS",
    8: "PPS",
    9: "AUD",
    10: "END_OF_SEQUENCE",
    11: "END_OF_STREAM",
    12: "FILLER_DATA",
}

H265_NAL_NAMES: dict[int, str] = {
    0: "TRAIL_N",
    1: "TRAIL_R",
    19: "IDR_W_RADL",
    20: "IDR_N_LP",
    21: "CRA_NUT",
    32: "VPS",
    33: "SPS",
    34: "PPS",
    35: "AUD",
    39: "PREFIX_SEI",
    40: "SUFFIX_SEI",
}

# H.264 IDR types
_H264_IDR_TYPES: frozenset[int] = frozenset({5})
_H264_PARAM_SET_TYPES: frozenset[int] = frozenset({7, 8})   # SPS, PPS
_H264_SLICE_TYPES: frozenset[int] = frozenset({1, 2, 3, 4, 5})

# H.265 IRAP types (IDR + CRA)
_H265_IRAP_TYPES: frozenset[int] = frozenset({19, 20, 21})
_H265_PARAM_SET_TYPES: frozenset[int] = frozenset({32, 33, 34})  # VPS, SPS, PPS


# ──────────────────────────────────────────────────────────────────────────────
# NALUnit
# ──────────────────────────────────────────────────────────────────────────────

class NALUnit(NamedTuple):
    """Carved NAL unit metadata and stream offset."""

    start_offset: int
    payload_offset: int
    prefix_length: int
    header_byte: int
    h264_type: int
    h264_name: str
    h265_type: int
    h265_name: str

    # ── Convenience predicates ──────────────────────────────────────────────

    def is_h264_idr(self) -> bool:
        return self.h264_type in _H264_IDR_TYPES

    def is_h264_param_set(self) -> bool:
        return self.h264_type in _H264_PARAM_SET_TYPES

    def is_h265_irap(self) -> bool:
        return self.h265_type in _H265_IRAP_TYPES

    def is_h265_param_set(self) -> bool:
        return self.h265_type in _H265_PARAM_SET_TYPES


# ──────────────────────────────────────────────────────────────────────────────
# SegmentRecord — GOP-level recovery unit
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SegmentRecord:
    """A recovered video segment (typically one GOP) with carving metadata.

    Attributes:
        offset:      Byte offset of first NAL unit in the source stream / image.
        length:      Byte span from offset to end of last NAL unit in segment.
        codec:       Detected codec: "h264", "h265", or "unknown".
        gop_index:   Zero-based sequential index of this GOP in the carved stream.
        has_sps:     True if an SPS (H.264) or SPS+VPS (H.265) NAL is present.
        has_pps:     True if a PPS NAL is present.
        has_idr:     True if an IDR / IRAP NAL is present.
        nal_count:   Total number of NAL units in this segment.
        confidence:  0.0–1.0 quality score (1.0 = complete, decodable GOP).
        repaired:    True if SPS/PPS were borrowed from a neighbour by gop_repair.
        nal_units:   Ordered list of NALUnit objects belonging to this segment.
    """

    offset: int
    length: int
    codec: str
    gop_index: int
    has_sps: bool = False
    has_pps: bool = False
    has_idr: bool = False
    nal_count: int = 0
    confidence: float = 0.0
    repaired: bool = False
    nal_units: list[NALUnit] = field(default_factory=list)

    def compute_confidence(self) -> None:
        """Recompute confidence score from structural completeness.

        Score:
            +0.4  has_idr
            +0.3  has_sps
            +0.2  has_pps
            +0.1  nal_count >= 2
            Penalty: ×0.5 if repaired (set by gop_repair externally)
        """
        score = 0.0
        if self.has_idr:
            score += 0.4
        if self.has_sps:
            score += 0.3
        if self.has_pps:
            score += 0.2
        if self.nal_count >= 2:
            score += 0.1
        self.confidence = round(score, 3)


# ──────────────────────────────────────────────────────────────────────────────
# Abstract carver interface
# ──────────────────────────────────────────────────────────────────────────────

class BaseNALCarver(ABC):
    """Abstract interface for high-performance Annex-B carving."""

    @abstractmethod
    def carve_bytes(self, data: bytes, base_offset: int = 0) -> list[NALUnit]:
        """Carve NAL units from in-memory byte buffer."""
        raise NotImplementedError

    @abstractmethod
    def carve_stream(
        self, stream: BinaryIO | BufferedReader, chunk_size: int = 65536
    ) -> Generator[NALUnit, None, None]:
        """Carve NAL units from streaming file or device descriptor."""
        raise NotImplementedError


# ──────────────────────────────────────────────────────────────────────────────
# Pure-Python implementation
# ──────────────────────────────────────────────────────────────────────────────

class PythonAnnexBCarver(BaseNALCarver):
    """Pure-Python streaming Annex-B start code carver."""

    def carve_bytes(self, data: bytes, base_offset: int = 0) -> list[NALUnit]:
        """Scan buffer for Annex-B start codes and parse NAL unit headers."""
        results: list[NALUnit] = []
        n = len(data)
        if n < 4:
            return results

        i = 0
        while i < n - 3:
            if data[i] == 0 and data[i + 1] == 0:
                if data[i + 2] == 1:
                    # 3-byte prefix: 00 00 01
                    prefix_len = 3
                    nal_byte_idx = i + 3
                    if nal_byte_idx < n:
                        header_byte = data[nal_byte_idx]
                        h264_type = header_byte & 0x1F
                        h265_type = (header_byte >> 1) & 0x3F
                        results.append(
                            NALUnit(
                                start_offset=base_offset + i,
                                payload_offset=base_offset + nal_byte_idx,
                                prefix_length=prefix_len,
                                header_byte=header_byte,
                                h264_type=h264_type,
                                h264_name=H264_NAL_NAMES.get(h264_type, f"TYPE_{h264_type}"),
                                h265_type=h265_type,
                                h265_name=H265_NAL_NAMES.get(h265_type, f"TYPE_{h265_type}"),
                            )
                        )
                    i += 3
                    continue
                elif data[i + 2] == 0 and i + 3 < n and data[i + 3] == 1:
                    # 4-byte prefix: 00 00 00 01
                    prefix_len = 4
                    nal_byte_idx = i + 4
                    if nal_byte_idx < n:
                        header_byte = data[nal_byte_idx]
                        h264_type = header_byte & 0x1F
                        h265_type = (header_byte >> 1) & 0x3F
                        results.append(
                            NALUnit(
                                start_offset=base_offset + i,
                                payload_offset=base_offset + nal_byte_idx,
                                prefix_length=prefix_len,
                                header_byte=header_byte,
                                h264_type=h264_type,
                                h264_name=H264_NAL_NAMES.get(h264_type, f"TYPE_{h264_type}"),
                                h265_type=h265_type,
                                h265_name=H265_NAL_NAMES.get(h265_type, f"TYPE_{h265_type}"),
                            )
                        )
                    i += 4
                    continue
            i += 1

        return results

    def carve_stream(
        self, stream: BinaryIO | BufferedReader, chunk_size: int = 65536
    ) -> Generator[NALUnit, None, None]:
        """Carve NAL units from a chunked stream with 8-byte overlap to prevent boundary cuts."""
        overlap_size = 8
        buffer = b""
        current_base_offset = 0

        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                if buffer:
                    yield from self.carve_bytes(buffer, base_offset=current_base_offset)
                break

            combined = buffer + chunk
            units = self.carve_bytes(combined, base_offset=current_base_offset)
            cutoff_offset = current_base_offset + len(combined) - overlap_size

            for unit in units:
                if unit.start_offset < cutoff_offset:
                    yield unit

            if len(combined) >= overlap_size:
                buffer = combined[-overlap_size:]
                current_base_offset += len(combined) - overlap_size
            else:
                buffer = combined
                current_base_offset += len(combined)


# ──────────────────────────────────────────────────────────────────────────────
# GOP grouping
# ──────────────────────────────────────────────────────────────────────────────

def _detect_codec(nal_units: list[NALUnit]) -> str:
    """Heuristically detect codec from NAL type distribution.

    H.265 has VPS (type 32), which H.264 lacks.  If a VPS is present we
    call it H.265.  If SPS (type 7 in H.264 / type 33 in H.265 via h265_type)
    is found alongside IDR (type 5 h264) → H.264.  Otherwise 'unknown'.
    """
    for u in nal_units:
        if u.h265_type == 32:   # VPS
            return "h265"
    for u in nal_units:
        if u.h264_type in {5, 7, 8}:  # IDR, SPS, PPS (H.264 specific values)
            return "h264"
    return "unknown"


def group_into_gops(
    nal_units: list[NALUnit],
    stream_data: bytes | None = None,
) -> list[SegmentRecord]:
    """Group a flat list of NALUnit objects into GOP-level SegmentRecords.

    A new GOP begins at each IDR / IRAP NAL unit.  Any leading NAL units
    before the first IDR are collected into a preamble segment (gop_index=-1).

    Args:
        nal_units:   Flat ordered list of carved NAL units.
        stream_data: Optional source bytes (used only for length computation of
                     the last NAL unit; if None, lengths are estimated from
                     offsets between consecutive starts).

    Returns:
        List of SegmentRecord objects in offset order.  Empty if nal_units is empty.
    """
    if not nal_units:
        return []

    # Compute the end offset of each NAL unit as the start of the next one
    # (or stream end for the last).
    stream_end = len(stream_data) if stream_data is not None else -1

    def _end_offset(idx: int) -> int:
        if idx + 1 < len(nal_units):
            return nal_units[idx + 1].start_offset
        if stream_end >= 0:
            return stream_end
        # Estimate: add a small fixed size for the last NAL
        return nal_units[idx].start_offset + 4

    # Split at IDR / IRAP boundaries
    groups: list[list[int]] = []        # each group = list of indices into nal_units
    current_group: list[int] = []

    for idx, u in enumerate(nal_units):
        is_idr_h264 = u.h264_type in _H264_IDR_TYPES
        is_irap_h265 = u.h265_type in _H265_IRAP_TYPES

        if (is_idr_h264 or is_irap_h265) and current_group:
            # Look back: if SPS/PPS immediately precede this IDR, include them
            # in the current (new) group by flushing the old group minus those
            param_lookback: list[int] = []
            while (
                current_group
                and nal_units[current_group[-1]].h264_type in _H264_PARAM_SET_TYPES
                or (
                    current_group
                    and nal_units[current_group[-1]].h265_type in _H265_PARAM_SET_TYPES
                )
            ):
                param_lookback.insert(0, current_group.pop())

            if current_group:
                groups.append(current_group)
            current_group = param_lookback

        current_group.append(idx)

    if current_group:
        groups.append(current_group)

    # Build SegmentRecord for each group
    records: list[SegmentRecord] = []
    gop_counter = 0

    for grp in groups:
        first = nal_units[grp[0]]
        last_idx = grp[-1]
        seg_end = _end_offset(last_idx)
        length = max(1, seg_end - first.start_offset)

        h264_types = {nal_units[i].h264_type for i in grp}
        h265_types = {nal_units[i].h265_type for i in grp}

        has_idr = bool(h264_types & _H264_IDR_TYPES or h265_types & _H265_IRAP_TYPES)
        has_sps = bool(
            7 in h264_types            # H.264 SPS
            or 33 in h265_types        # H.265 SPS
            or 32 in h265_types        # H.265 VPS (treat as equivalent for scoring)
        )
        has_pps = bool(8 in h264_types or 34 in h265_types)

        codec = _detect_codec([nal_units[i] for i in grp])

        seg = SegmentRecord(
            offset=first.start_offset,
            length=length,
            codec=codec,
            gop_index=gop_counter,
            has_sps=has_sps,
            has_pps=has_pps,
            has_idr=has_idr,
            nal_count=len(grp),
            nal_units=[nal_units[i] for i in grp],
        )
        seg.compute_confidence()
        records.append(seg)
        if has_idr:
            gop_counter += 1

    return records


# ──────────────────────────────────────────────────────────────────────────────
# Default singleton
# ──────────────────────────────────────────────────────────────────────────────

default_nal_carver = PythonAnnexBCarver()
