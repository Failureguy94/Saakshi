"""FrameProof Annex-B NAL Carver (H.264 / H.265).

Purpose: Scan raw binary streams or disk images for Annex-B start codes (00 00 01 / 00 00 00 01),
         extract NAL unit headers, and classify NAL types across H.264 (AVC) and H.265 (HEVC).
Inputs: Binary streams or raw byte sequences.
Outputs: Structured stream of carved NAL units with precise offsets, header types, and classifications.
Status: Implemented (Python backend; designed with interface for Rust acceleration).
"""

from abc import ABC, abstractmethod
from collections.abc import Generator
from io import BufferedReader
from typing import BinaryIO, NamedTuple

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
            # Check for 0x00 0x00 0x01 (3-byte) or 0x00 0x00 0x00 0x01 (4-byte)
            if data[i] == 0 and data[i + 1] == 0:
                if data[i + 2] == 1:
                    # 3-byte prefix: 00 00 01
                    prefix_len = 3
                    # Check if preceded by an extra zero byte (e.g. 00 00 00 01)
                    if i > 0 and data[i - 1] == 0 and (not results or results[-1].start_offset != base_offset + i - 1):
                        # Part of a 4-byte sequence already handled or separate
                        pass
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
                # Flush remainder
                if buffer:
                    for unit in self.carve_bytes(buffer, base_offset=current_base_offset):
                        yield unit
                break

            combined = buffer + chunk
            # Find units within combined buffer
            units = self.carve_bytes(combined, base_offset=current_base_offset)

            # Yield units whose start_offset is strictly before the end of the reliable chunk boundary
            cutoff_offset = current_base_offset + len(combined) - overlap_size

            for unit in units:
                if unit.start_offset < cutoff_offset:
                    yield unit

            # Carry over the last overlap_size bytes
            if len(combined) >= overlap_size:
                buffer = combined[-overlap_size:]
                current_base_offset += len(combined) - overlap_size
            else:
                buffer = combined
                current_base_offset += len(combined)


# Default carver singleton
default_nal_carver = PythonAnnexBCarver()
