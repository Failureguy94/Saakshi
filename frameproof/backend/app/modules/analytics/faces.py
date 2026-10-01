"""FrameProof Facial Feature Extractor & Re-Identification.

Purpose: Detect human faces, generate biometric embeddings, and perform cross-camera re-identification.
Inputs: Video frames containing human subjects.
Outputs: Facial bounding boxes, confidence scores, and feature embedding vectors.
Status: Stub
"""

from pathlib import Path
from typing import Any


class FacialFeatureExtractor:
    """Facial feature extractor and cross-camera matching engine (planned)."""

    def __init__(self) -> None:
        pass

    def extract_faces(self, frame_path: Path | str) -> list[dict[str, Any]]:
        """Extract face bounding boxes and embeddings from frame.

        Raises:
            NotImplementedError: Face detection and embedding extraction is planned.
        """
        raise NotImplementedError("planned: facial recognition embedding extraction and re-identification")
