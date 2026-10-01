"""FrameProof On-Screen Display (OSD) OCR Engine.

Purpose: Detect and extract burnt-in camera timestamps, channel names, and watermarks via OCR.
Inputs: Decoded raw video frame bitmaps or image tensors.
Outputs: Parsed text strings, timestamps, and bounding box coordinates.
Status: Stub
"""

from datetime import datetime
from pathlib import Path


class OSDTimestampExtractor:
    """Extracts on-screen display timestamps from video frames (planned)."""

    def __init__(self) -> None:
        pass

    def extract_timestamp(self, frame_image_path: Path | str) -> datetime | None:
        """Run OCR on target frame region to extract burnt-in time.

        Raises:
            NotImplementedError: OSD timestamp extraction via optical character recognition is planned.
        """
        raise NotImplementedError("planned: OSD visual timestamp OCR extraction")
