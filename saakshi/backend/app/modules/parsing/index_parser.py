"""Saakshi DVR Index Table Parser.

Purpose: Extract recording catalog tables, timestamps, channel mappings, and file offsets.
Inputs: Volume handle, index sector offsets, and OEM profile.
Outputs: List of contiguous recording clip descriptors with start/end timestamps.
Status: Stub
"""

from pathlib import Path
from typing import Any

from app.modules.profiles.schema import VendorProfile


class IndexParser:
    """Parses DVR proprietary index tables and recording catalogs (planned)."""

    def __init__(self, profile: VendorProfile) -> None:
        self.profile = profile

    def extract_index_entries(self, evidence_path: Path | str) -> list[dict[str, Any]]:
        """Extract recording index table entries.

        Raises:
            NotImplementedError: Proprietary index table parsing is planned.
        """
        raise NotImplementedError("planned: proprietary DVR index table and catalog extraction")
