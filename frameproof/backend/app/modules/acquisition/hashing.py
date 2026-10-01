"""FrameProof Forensic Dual Streaming Hasher.

Purpose: Compute simultaneous cryptographic digests (MD5 and SHA-256) in a single pass
         over a byte stream or raw file without mutating the source media.
Inputs: File path, open binary stream, or byte iterator.
Outputs: HashResult containing MD5 hex string, SHA-256 hex string, and total byte count.
Status: Implemented
"""

import hashlib
from io import BufferedReader
from pathlib import Path
from typing import BinaryIO, NamedTuple

from app.core.security import ReadOnlySecurityGuard


class HashResult(NamedTuple):
    """Immutable result of a dual hashing pass."""

    md5: str
    sha256: str
    byte_count: int


def hash_stream(
    stream: BinaryIO | BufferedReader,
    chunk_size: int = 65536,
) -> HashResult:
    """Compute MD5 and SHA-256 digests in a single pass over an open binary stream.

    Args:
        stream: Readable binary stream.
        chunk_size: Read buffer size in bytes (default: 64KB).

    Returns:
        HashResult containing hex digests and total byte count.
    """
    md5_ctx = hashlib.md5()
    sha256_ctx = hashlib.sha256()
    total_bytes = 0

    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        md5_ctx.update(chunk)
        sha256_ctx.update(chunk)
        total_bytes += len(chunk)

    return HashResult(
        md5=md5_ctx.hexdigest(),
        sha256=sha256_ctx.hexdigest(),
        byte_count=total_bytes,
    )


def hash_file(
    file_path: Path | str,
    chunk_size: int = 65536,
) -> HashResult:
    """Verify read-only accessibility and compute dual digests for an evidence file.

    Args:
        file_path: Path to the target evidence file.
        chunk_size: Read buffer size in bytes (default: 64KB).

    Returns:
        HashResult containing hex digests and total byte count.
    """
    path = Path(file_path)
    ReadOnlySecurityGuard.assert_read_only_path(path)

    with open(path, "rb") as f:
        return hash_stream(f, chunk_size=chunk_size)
