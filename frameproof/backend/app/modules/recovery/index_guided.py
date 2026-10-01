"""FrameProof Index-Guided Stream Recovery.

Purpose: Extract and verify video clips based on parsed index table pointers.
Inputs: Read-only evidence image, parsed index records, and target destination directory.
Outputs: Extracted and validated video segment files.
Status: Stub
"""

from pathlib import Path
from typing import Any


class IndexGuidedRecovery:
    """Extracts video streams guided by file allocation records (planned)."""

    def __init__(self) -> None:
        pass

    def recover_clips(
        self,
        evidence_path: Path | str,
        index_records: list[dict[str, Any]],
        output_dir: Path | str,
    ) -> list[Path]:
        """Recover referenced clips from disk image.

        Raises:
            NotImplementedError: Index-guided extraction is planned.
        """
        raise NotImplementedError("planned: index-guided video segment carving and export")
