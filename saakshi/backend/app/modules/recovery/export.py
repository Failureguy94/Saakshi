"""Saakshi Recovery Export Module.

Purpose:
    Remux each recovered SegmentRecord (raw Annex-B byte stream) into a
    standards-compliant .mp4 container using ffmpeg with no re-encode
    (-c copy).  Computes SHA-256 of each exported clip and writes a
    custody log entry per clip.

    If ffmpeg is not available the module raises ExportError with a clear
    message so the caller can degrade gracefully.

Inputs:
    List[SegmentRecord], raw source bytes, output directory, CustodyLog.

Outputs:
    List[ExportedClip] – mp4 path, sha256, byte_count, metadata.
    Custody entries in the provided CustodyLog.

Status: Implemented (requires ffmpeg on PATH; raises ExportError otherwise).
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.modules.custody.chain import CustodyLog
from app.modules.recovery.nal_carver import SegmentRecord


class ExportError(RuntimeError):
    """Raised when a clip cannot be exported (ffmpeg missing, remux failure, etc.)."""


@dataclass
class ExportedClip:
    """Metadata for one successfully exported .mp4 clip.

    Attributes:
        segment:      Source SegmentRecord that was exported.
        mp4_path:     Absolute path to the exported .mp4 file.
        sha256:       SHA-256 hex digest of the .mp4 file.
        byte_count:   File size in bytes.
        ffmpeg_ok:    True if ffmpeg remux completed without error.
        custody_seq:  Sequence number assigned in the custody log.
    """

    segment: SegmentRecord
    mp4_path: Path
    sha256: str
    byte_count: int
    ffmpeg_ok: bool
    custody_seq: int


def _require_ffmpeg() -> str:
    """Return the path to ffmpeg binary or raise ExportError."""
    binary = shutil.which("ffmpeg")
    if binary is None:
        raise ExportError(
            "ffmpeg is not installed or not on PATH.  "
            "Install it with: sudo apt install ffmpeg  (or equivalent)."
        )
    return binary


def _sha256_file(path: Path) -> tuple[str, int]:
    """Compute SHA-256 and size of a file in a single streaming pass."""
    ctx = hashlib.sha256()
    total = 0
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            ctx.update(chunk)
            total += len(chunk)
    return ctx.hexdigest(), total


def _remux_annexb_to_mp4(
    ffmpeg: str,
    source_file: Path,
    codec: str,
    out_path: Path,
) -> bool:
    """Call ffmpeg to remux Annex-B bitstream into .mp4 (no re-encode).

    Args:
        ffmpeg:      Path to ffmpeg binary.
        source_file: Temporary file containing the raw Annex-B bytes.
        codec:       "h264" or "h265" (selects the input format).
        out_path:    Destination .mp4 path.

    Returns:
        True on success, False on ffmpeg error.
    """
    input_fmt = "h264" if codec != "h265" else "hevc"
    cmd = [
        ffmpeg,
        "-y",
        "-f", input_fmt,
        "-i", str(source_file),
        "-c", "copy",
        "-movflags", "+faststart",
        str(out_path),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        timeout=120,
    )
    return result.returncode == 0


def export_segments(
    segments: list[SegmentRecord],
    source_data: bytes,
    out_dir: Path,
    custody_log: CustodyLog | None = None,
    actor: str = "saakshi_exporter",
    case_id: str = "UNKNOWN",
    skip_missing_params: bool = False,
) -> list[ExportedClip]:
    """Remux recovered SegmentRecords into .mp4 clips.

    Each segment's raw Annex-B bytes are extracted from source_data, written
    to a temporary file, then fed to ffmpeg -c copy for containerisation.
    The resulting .mp4 is hashed and a custody entry is written.

    Args:
        segments:            List of SegmentRecord (from nal_carver or gop_repair).
        source_data:         Full raw bytes of the disk image / stream.
        out_dir:             Directory where .mp4 files are written.
        custody_log:         CustodyLog to append entries to (optional).
        actor:               Actor string for custody entries.
        case_id:             Case identifier for custody metadata.
        skip_missing_params: If True, skip segments without SPS/PPS instead of
                             raising ExportError.

    Returns:
        List of ExportedClip for every successfully exported segment.

    Raises:
        ExportError: if ffmpeg is not available.
    """
    ffmpeg = _require_ffmpeg()
    out_dir.mkdir(parents=True, exist_ok=True)
    exported: list[ExportedClip] = []
    seq = 0

    for seg in segments:
        if skip_missing_params and (not seg.has_sps or not seg.has_pps):
            continue

        # Extract raw Annex-B bytes for this segment
        end = seg.offset + seg.length
        raw = source_data[seg.offset:end]
        if not raw:
            continue

        # Write to temp file
        suffix = ".h265" if seg.codec == "h265" else ".h264"
        mp4_name = f"gop_{seg.gop_index:05d}_{seg.codec}.mp4"
        mp4_path = out_dir / mp4_name

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(raw)

        try:
            ok = _remux_annexb_to_mp4(
                ffmpeg=ffmpeg,
                source_file=tmp_path,
                codec=seg.codec,
                out_path=mp4_path,
            )
        finally:
            tmp_path.unlink(missing_ok=True)

        if not ok or not mp4_path.exists():
            continue

        digest, size = _sha256_file(mp4_path)

        if custody_log is not None:
            custody_log.append(
                actor=actor,
                action="EXPORT_CLIP",
                evidence_id=str(mp4_path),
                evidence_hash=digest,
                details={
                    "case_id": case_id,
                    "gop_index": seg.gop_index,
                    "codec": seg.codec,
                    "source_offset": seg.offset,
                    "source_length": seg.length,
                    "confidence": seg.confidence,
                    "repaired": seg.repaired,
                    "mp4_path": str(mp4_path),
                    "sha256": digest,
                    "byte_count": size,
                },
            )

        exported.append(
            ExportedClip(
                segment=seg,
                mp4_path=mp4_path,
                sha256=digest,
                byte_count=size,
                ffmpeg_ok=ok,
                custody_seq=seq,
            )
        )
        seq += 1

    return exported
