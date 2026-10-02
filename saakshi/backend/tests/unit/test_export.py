"""Tests for recovery/export.py.

Because ffmpeg may not be installed in the test environment, we:
1. Test that ExportError is raised cleanly when ffmpeg is absent.
2. Mock ffmpeg to verify the correct argument shapes are called.
3. Test _sha256_file independently.

Status: Tests for implemented functionality (ffmpeg-dependent paths use mocks).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.modules.recovery.export import ExportError, _sha256_file, export_segments
from app.modules.recovery.nal_carver import default_nal_carver, group_into_gops


def _nal(header_byte: int, payload: bytes = b"\x00" * 16) -> bytes:
    return b"\x00\x00\x00\x01" + bytes([header_byte]) + payload


def _h264_gop() -> bytes:
    return _nal(0x67) + _nal(0x68) + _nal(0x65, b"\xAB" * 64) + _nal(0x61)


class TestSha256File:
    def test_sha256_matches_hashlib(self, tmp_path: Path) -> None:
        data = b"hello forensics " * 1000
        f = tmp_path / "test.bin"
        f.write_bytes(data)
        digest, size = _sha256_file(f)
        expected = hashlib.sha256(data).hexdigest()
        assert digest == expected
        assert size == len(data)

    def test_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.bin"
        f.write_bytes(b"")
        digest, size = _sha256_file(f)
        assert size == 0
        assert digest == hashlib.sha256(b"").hexdigest()


class TestExportNoFfmpeg:
    """Tests when ffmpeg is not available."""

    def test_require_ffmpeg_raises_export_error(self) -> None:
        with patch("shutil.which", return_value=None):
            from app.modules.recovery.export import _require_ffmpeg
            with pytest.raises(ExportError, match="ffmpeg"):
                _require_ffmpeg()

    def test_export_segments_raises_export_error(self, tmp_path: Path) -> None:
        data = _h264_gop()
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)
        with patch("shutil.which", return_value=None), pytest.raises(ExportError):
            export_segments(segs, data, tmp_path)


class TestExportWithMockedFfmpeg:
    """Tests that mock ffmpeg to verify correct CLI argument construction."""

    def _make_mp4(self, path: Path) -> None:
        """Create a minimal fake .mp4 so _sha256_file succeeds."""
        path.write_bytes(b"\x00" * 128)

    def test_export_single_segment_calls_ffmpeg(self, tmp_path: Path) -> None:
        data = _h264_gop()
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)

        if not segs:
            pytest.skip("No segments carved from minimal GOP")

        with (
            patch("shutil.which", return_value="/usr/bin/ffmpeg"),
            patch("subprocess.run") as mock_run,
        ):
            def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
                # Simulate ffmpeg success: create the output file
                out_path = Path(cmd[-1])
                out_path.write_bytes(b"\x00" * 256)
                m = MagicMock()
                m.returncode = 0
                return m

            mock_run.side_effect = fake_run
            result = export_segments(segs, data, tmp_path)

        assert len(result) >= 1
        clip = result[0]
        assert clip.ffmpeg_ok is True
        assert clip.mp4_path.exists()
        assert len(clip.sha256) == 64  # sha256 hex digest

    def test_export_writes_custody_entries(self, tmp_path: Path) -> None:
        from app.modules.custody.chain import CustodyLog

        data = _h264_gop()
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)

        if not segs:
            pytest.skip("No segments carved")

        custody_log = CustodyLog(log_path=tmp_path / "custody.jsonl")

        with (
            patch("shutil.which", return_value="/usr/bin/ffmpeg"),
            patch("subprocess.run") as mock_run,
        ):
            def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
                Path(cmd[-1]).write_bytes(b"\x00" * 64)
                m = MagicMock()
                m.returncode = 0
                return m

            mock_run.side_effect = fake_run
            export_segments(segs, data, tmp_path, custody_log=custody_log)

        ok, _ = custody_log.verify()
        assert ok

    def test_ffmpeg_failure_skips_segment(self, tmp_path: Path) -> None:
        data = _h264_gop()
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)

        if not segs:
            pytest.skip("No segments")

        with (
            patch("shutil.which", return_value="/usr/bin/ffmpeg"),
            patch("subprocess.run") as mock_run,
        ):
            m = MagicMock()
            m.returncode = 1   # simulate ffmpeg failure
            mock_run.return_value = m
            result = export_segments(segs, data, tmp_path)

        # No clips should be exported on ffmpeg failure
        assert result == []

    def test_h265_uses_hevc_format(self, tmp_path: Path) -> None:
        # H.265 GOP
        def _nal_h265(header_byte: int) -> bytes:
            return b"\x00\x00\x00\x01" + bytes([header_byte]) + b"\x00" * 16

        data = _nal_h265(0x40) + _nal_h265(0x42) + _nal_h265(0x44) + _nal_h265(0x26)
        nals = default_nal_carver.carve_bytes(data)
        segs = group_into_gops(nals, stream_data=data)

        if not segs:
            pytest.skip("No H.265 segments carved")

        called_cmds: list[list[str]] = []

        with (
            patch("shutil.which", return_value="/usr/bin/ffmpeg"),
            patch("subprocess.run") as mock_run,
        ):
            def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
                called_cmds.append(cmd)
                Path(cmd[-1]).write_bytes(b"\x00" * 64)
                m = MagicMock()
                m.returncode = 0
                return m

            mock_run.side_effect = fake_run
            export_segments(segs, data, tmp_path)

        if called_cmds:
            # -f hevc should appear in the command for H.265
            assert "hevc" in called_cmds[0]
