"""Tests for acquisition/cli.py — saakshi acquire and verify commands.

Status: Tests for implemented CLI.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from app.modules.acquisition.cli import cli


@pytest.fixture()
def small_image(tmp_path: Path) -> Path:
    """Create a small synthetic disk image for testing."""
    img = tmp_path / "test.img"
    # Write deterministic content
    img.write_bytes(b"\x00\x00\x00\x01" * 100 + b"\xff" * 100)
    return img


class TestAcquireCommand:
    def test_acquire_outputs_md5_sha256(self, small_image: Path, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["acquire", str(small_image), "--out-dir", str(tmp_path), "--case-id", "CASE001"],
        )
        assert result.exit_code == 0, result.output
        assert "MD5" in result.output
        assert "SHA-256" in result.output
        assert "CASE001" not in result.output  # case_id goes to custody log, not stdout

    def test_acquire_json_output(self, small_image: Path, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["acquire", str(small_image), "--out-dir", str(tmp_path), "--json-output"],
        )
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "md5" in data
        assert "sha256" in data
        assert "byte_count" in data
        assert data["byte_count"] == 500  # 400 + 100 bytes

    def test_acquire_writes_custody_log(self, small_image: Path, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["acquire", str(small_image), "--out-dir", str(tmp_path)],
        )
        assert result.exit_code == 0, result.output
        log_file = tmp_path / "custody.jsonl"
        assert log_file.exists()
        lines = log_file.read_text().strip().splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["action"] == "ACQUIRE"

    def test_acquire_custom_log_file(self, small_image: Path, tmp_path: Path) -> None:
        custom_log = tmp_path / "custom.jsonl"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["acquire", str(small_image), "--log-file", str(custom_log)],
        )
        assert result.exit_code == 0, result.output
        assert custom_log.exists()

    def test_verify_mode_correct_hash_passes(self, small_image: Path, tmp_path: Path) -> None:
        runner = CliRunner()
        # First pass to get digests
        first = runner.invoke(
            cli,
            ["acquire", str(small_image), "--out-dir", str(tmp_path), "--json-output"],
        )
        assert first.exit_code == 0
        data = json.loads(first.output)

        # Second pass with correct hashes
        result = runner.invoke(
            cli,
            [
                "acquire", str(small_image),
                "--out-dir", str(tmp_path),
                "--verify-md5", data["md5"],
                "--verify-sha256", data["sha256"],
            ],
        )
        assert result.exit_code == 0
        assert "VERIFIED" in result.output

    def test_verify_mode_wrong_md5_fails(self, small_image: Path, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "acquire", str(small_image),
                "--out-dir", str(tmp_path),
                "--verify-md5", "deadbeef" * 4,   # wrong hash
            ],
        )
        assert result.exit_code == 1
        assert "MISMATCH" in result.output

    def test_acquire_nonexistent_file_exits_1(self, tmp_path: Path) -> None:
        runner = CliRunner()
        # Click will catch missing path before our code runs
        result = runner.invoke(cli, ["acquire", "/nonexistent/path/to/image.img"])
        assert result.exit_code != 0


class TestVerifyCommand:
    def test_verify_valid_chain_passes(self, small_image: Path, tmp_path: Path) -> None:
        runner = CliRunner()
        # Create custody log via acquire
        runner.invoke(cli, ["acquire", str(small_image), "--out-dir", str(tmp_path)])
        log = tmp_path / "custody.jsonl"
        result = runner.invoke(cli, ["verify", str(log)])
        assert result.exit_code == 0
        assert "VALID" in result.output

    def test_verify_tampered_chain_fails(self, small_image: Path, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["acquire", str(small_image), "--out-dir", str(tmp_path)])
        log = tmp_path / "custody.jsonl"
        # Tamper with the log
        content = log.read_text()
        tampered = content.replace("ACQUIRE", "TAMPERED_ACQUIRE")
        log.write_text(tampered)
        result = runner.invoke(cli, ["verify", str(log)])
        # Either exit code 1 is set, or an exception was raised (ValueError from chain validation)
        # In both cases the chain must not be considered valid
        assert result.exit_code == 1 or result.exception is not None

    def test_verify_json_output(self, small_image: Path, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["acquire", str(small_image), "--out-dir", str(tmp_path)])
        log = tmp_path / "custody.jsonl"
        result = runner.invoke(cli, ["verify", str(log), "--json-output"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["chain_valid"] is True
