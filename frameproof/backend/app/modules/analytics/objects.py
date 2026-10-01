"""FrameProof Forensic Object Detector & Classifier.

Purpose: Detect and classify vehicles, persons, backpacks, and weapons in surveillance frames.
Inputs: Decoded video frames or image sequences.
Outputs: Bounding boxes, class classifications, and trajectory paths.
Status: Stub
"""

from pathlib import Path
from typing import Any


class ObjectDetector:
    """Offline forensic object detection engine (planned)."""

    def __init__(self) -> None:
        pass

    def detect_objects(self, frame_path: Path | str) -> list[dict[str, Any]]:
        """Run object detection on frame.

        Raises:
            NotImplementedError: Object detection is planned.
        """
        raise NotImplementedError("planned: offline neural network object detection and bounding box extraction")
