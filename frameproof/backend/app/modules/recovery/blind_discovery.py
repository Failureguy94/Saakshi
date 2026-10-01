"""FrameProof Blind Stream Discovery.

Purpose: Carve video streams from uncharacterized disks without an OEM profile or filesystem structure.
Inputs: Read-only raw disk image.
Outputs: Discovered channel streams, resolution groupings, and codec profiles.
Status: Stub
"""

from pathlib import Path
from typing import Any


class BlindStreamDiscoverer:
    """Discovers and clusters video streams purely from raw NAL statistics (planned)."""

    def __init__(self) -> None:
        pass

    def discover_channels(self, evidence_path: Path | str) -> list[dict[str, Any]]:
        """Scan entire disk and cluster NAL sequences into coherent camera channels.

        Raises:
            NotImplementedError: Blind stream clustering is planned.
        """
        raise NotImplementedError("planned: blind video stream discovery and channel clustering")
