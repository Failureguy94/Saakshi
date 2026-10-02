"""Saakshi GOP Repair Module.

Purpose:
    For SegmentRecords that are missing SPS and/or PPS parameter sets (i.e. the
    GOP starts mid-stream or the index was damaged), borrow the most recent
    complete parameter sets from the nearest valid neighbouring segment on the
    same codec stream and prepend them.  Marks the result as 'repaired' with a
    lower confidence score (original × 0.7) to preserve forensic honesty.

Inputs:
    List[SegmentRecord] from nal_carver.group_into_gops().
    Optional source bytes (used to extract raw NAL payloads for prepending).

Outputs:
    New list[SegmentRecord] with repaired segments inserted in place (the
    original list is not mutated).

Status: Implemented.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from app.modules.recovery.nal_carver import NALUnit, SegmentRecord

_H264_SPS = 7
_H264_PPS = 8
_H265_VPS = 32
_H265_SPS = 33
_H265_PPS = 34

# Annex-B 4-byte start code
_START_CODE = b"\x00\x00\x00\x01"

REPAIR_CONFIDENCE_MULTIPLIER = 0.7


@dataclass
class RepairResult:
    """Summary of a GOP repair pass.

    Attributes:
        segments:         Resulting list of SegmentRecord (repaired and original).
        repaired_count:   Number of segments that received borrowed parameter sets.
        unrepaired_count: Number of segments that needed repair but had no donor.
        total_input:      Total number of input segments.
    """

    segments: list[SegmentRecord] = field(default_factory=list)
    repaired_count: int = 0
    unrepaired_count: int = 0
    total_input: int = 0


def _extract_raw_nal(
    source: bytes,
    nal: NALUnit,
    next_nal_offset: int | None,
) -> bytes:
    """Extract the raw bytes (start code + header + payload) for a single NAL unit.

    Args:
        source:          Full source byte stream.
        nal:             NALUnit to extract.
        next_nal_offset: Byte offset of the next NAL unit (used as end boundary).
                         If None, extract to end of source.

    Returns:
        Raw bytes including the Annex-B start code.
    """
    end = next_nal_offset if next_nal_offset is not None else len(source)
    end = min(end, len(source))
    return source[nal.start_offset:end]


def _find_donor_param_sets(
    segments: list[SegmentRecord],
    target_idx: int,
    codec: str,
    source: bytes | None,
) -> tuple[list[bytes], list[NALUnit]]:
    """Search backwards then forwards for the nearest complete SPS+PPS donor.

    Args:
        segments:    Full ordered list of SegmentRecord.
        target_idx:  Index of the segment that needs repair.
        codec:       "h264" or "h265".
        source:      Raw source bytes (required to extract NAL payloads).

    Returns:
        Tuple of (list_of_raw_nal_bytes, list_of_donor_NALUnits).
        Both lists are empty if no suitable donor is found or source is None.
    """
    if source is None:
        return [], []

    param_types = (
        {_H264_SPS, _H264_PPS}
        if codec == "h264"
        else {_H265_VPS, _H265_SPS, _H265_PPS}
    )

    def _has_complete_params(seg: SegmentRecord) -> bool:
        types_in_seg = {u.h264_type for u in seg.nal_units}
        if codec == "h264":
            return {_H264_SPS, _H264_PPS}.issubset(types_in_seg)
        h265_types = {u.h265_type for u in seg.nal_units}
        return {_H265_SPS, _H265_PPS}.issubset(h265_types)

    # Search backward first (most common case: camera keeps SPS/PPS stable)
    for i in range(target_idx - 1, -1, -1):
        if segments[i].codec == codec and _has_complete_params(segments[i]):
            return _collect_param_nals(segments[i], param_types, codec, source)

    # Then forward
    for i in range(target_idx + 1, len(segments)):
        if segments[i].codec == codec and _has_complete_params(segments[i]):
            return _collect_param_nals(segments[i], param_types, codec, source)

    return [], []


def _collect_param_nals(
    seg: SegmentRecord,
    param_types: set[int],
    codec: str,
    source: bytes,
) -> tuple[list[bytes], list[NALUnit]]:
    """Extract raw bytes of SPS/PPS/VPS NAL units from a donor segment."""
    raw_payloads: list[bytes] = []
    donor_nals: list[NALUnit] = []

    for j, u in enumerate(seg.nal_units):
        relevant = (
            u.h264_type in param_types if codec == "h264"
            else u.h265_type in param_types
        )
        if not relevant:
            continue
        next_off = (
            seg.nal_units[j + 1].start_offset
            if j + 1 < len(seg.nal_units)
            else None
        )
        raw = _extract_raw_nal(source, u, next_off)
        if raw:
            raw_payloads.append(raw)
            donor_nals.append(u)

    return raw_payloads, donor_nals


def repair_gops(
    segments: list[SegmentRecord],
    source: bytes | None = None,
) -> RepairResult:
    """Run a single-pass GOP repair over a list of SegmentRecords.

    For each segment missing SPS and/or PPS:
    1. Search backwards then forwards for the nearest donor segment.
    2. If found and source bytes are available, prepend the raw NAL bytes.
    3. Mark the segment repaired=True and apply the confidence multiplier.
    4. If no donor is found, leave the segment as-is and increment unrepaired_count.

    Segments that already have complete parameter sets are returned unchanged.
    The input list is NOT mutated; a deep copy is returned.

    Args:
        segments:  Ordered list of SegmentRecord from group_into_gops().
        source:    Raw source bytes (disk image or stream data).  If None,
                   structural metadata is updated but no byte prepending occurs.

    Returns:
        RepairResult with the processed segment list and repair statistics.
    """
    result = RepairResult(total_input=len(segments))
    output: list[SegmentRecord] = []

    for idx, seg in enumerate(segments):
        needs_sps = not seg.has_sps
        needs_pps = not seg.has_pps
        needs_repair = (needs_sps or needs_pps) and seg.has_idr

        if not needs_repair:
            output.append(deepcopy(seg))
            continue

        # Attempt to find donor parameter sets
        donor_raw, donor_nals = _find_donor_param_sets(
            segments=segments,
            target_idx=idx,
            codec=seg.codec,
            source=source,
        )

        repaired_seg = deepcopy(seg)

        if donor_nals:
            # Prepend donor NAL units to the segment's nal_units list
            repaired_seg.nal_units = donor_nals + repaired_seg.nal_units
            repaired_seg.has_sps = True
            repaired_seg.has_pps = True
            repaired_seg.nal_count = len(repaired_seg.nal_units)

            # Extend the byte offset/length to encompass the prepended bytes
            if donor_raw and source is not None:
                total_prepend = sum(len(r) for r in donor_raw)
                repaired_seg.offset = max(0, repaired_seg.offset - total_prepend)
                repaired_seg.length += total_prepend

            repaired_seg.repaired = True
            repaired_seg.compute_confidence()
            repaired_seg.confidence = round(repaired_seg.confidence * REPAIR_CONFIDENCE_MULTIPLIER, 3)
            result.repaired_count += 1
        else:
            # No donor found — mark unrepaired, lower confidence slightly
            repaired_seg.confidence = round(seg.confidence * 0.5, 3)
            result.unrepaired_count += 1

        output.append(repaired_seg)

    result.segments = output
    return result
