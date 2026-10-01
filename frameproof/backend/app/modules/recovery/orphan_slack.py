"""FrameProof Orphan & Slack Space Carver.

Purpose: Harvest residual and unallocated slack sectors for fragmented surveillance video streams.
Inputs: Read-only evidence image and sector allocation bitmap.
Outputs: Orphaned video fragment streams and sector mapping reports.
Status: Stub
"""

from pathlib import Path


class OrphanSlackCarver:
    """Carves deleted or unindexed video fragments from volume slack (planned)."""

    def __init__(self, cluster_size: int = 4096) -> None:
        self.cluster_size = cluster_size

    def carve_slack(self, evidence_path: Path | str, unallocated_ranges: list[tuple[int, int]]) -> list[Path]:
        """Carve unallocated ranges for orphaned video segments.

        Raises:
            NotImplementedError: Slack space carving is planned.
        """
        raise NotImplementedError("planned: orphan sector and unallocated volume slack carving")
