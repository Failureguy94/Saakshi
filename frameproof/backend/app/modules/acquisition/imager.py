"""FrameProof Forensic Disk Imager.

Purpose: Create bit-stream disk images from physical disks or block devices with write-blocking.
Inputs: Source block device (/dev/sdX) or disk image path, destination path, and sector options.
Outputs: Image file and acquisition integrity certificate.
Status: Stub
"""

from pathlib import Path
from typing import NamedTuple


class ImagingReport(NamedTuple):
    """Forensic acquisition summary."""

    source_device: str
    target_path: Path
    bytes_written: int
    md5: str
    sha256: str


class ForensicImager:
    """Acquires raw bit-stream copies from physical media (planned)."""

    def __init__(self, buffer_size: int = 1048576) -> None:
        self.buffer_size = buffer_size

    def acquire(self, source_device: str, destination_path: Path | str) -> ImagingReport:
        """Execute bit-stream imaging pass.

        Raises:
            NotImplementedError: Direct physical block-level acquisition is planned.
        """
        raise NotImplementedError("planned: hardware write-blocked bit-stream disk acquisition")
