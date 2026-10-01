"""Saakshi Raw DD Image Reader.

Purpose: Provide read-only, random-access byte slicing over raw bit-stream (.raw, .dd, .img) files.
Inputs: File path and sector offsets.
Outputs: Read-only bytes buffers.
Status: Stub
"""

from pathlib import Path


class RawImageReader:
    """Read-only random access reader for raw bit-stream evidence images (planned)."""

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)

    def read_sector(self, sector_index: int, sector_size: int = 512) -> bytes:
        """Read specific sector from image.

        Raises:
            NotImplementedError: Raw sector slicing is planned.
        """
        raise NotImplementedError("planned: random access raw disk sector reader")
