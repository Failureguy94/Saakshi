"""Unit tests for acquisition dual-streaming hasher."""

import hashlib
import io
import tempfile
from pathlib import Path

import pytest

from app.modules.acquisition.hashing import hash_file, hash_stream


def test_hash_stream_consistency() -> None:
    data = b"Forensic surveillance sample raw data" * 1000
    expected_md5 = hashlib.md5(data).hexdigest()
    expected_sha256 = hashlib.sha256(data).hexdigest()

    stream = io.BytesIO(data)
    result = hash_stream(stream, chunk_size=128)

    assert result.byte_count == len(data)
    assert result.md5 == expected_md5
    assert result.sha256 == expected_sha256


def test_hash_empty_stream() -> None:
    stream = io.BytesIO(b"")
    result = hash_stream(stream)

    assert result.byte_count == 0
    assert result.md5 == hashlib.md5(b"").hexdigest()
    assert result.sha256 == hashlib.sha256(b"").hexdigest()


def test_hash_file_execution() -> None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Disk sector bit-stream chunk 12345")
        tmp_path = Path(tmp.name)

    try:
        res = hash_file(tmp_path)
        assert res.byte_count == 34
        assert len(res.md5) == 32
        assert len(res.sha256) == 64
    finally:
        tmp_path.unlink()


def test_hash_file_nonexistent_raises() -> None:
    with pytest.raises(FileNotFoundError):
        hash_file(Path("/nonexistent/path/evidence.raw"))
