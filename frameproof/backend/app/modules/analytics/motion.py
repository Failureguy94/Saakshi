"""FrameProof Motion Vector & Activity Analyzer.

Purpose: Detect motion events, vector trajectories, and macroblock changes in video streams.
Inputs: Video segment files or decoded frames.
Outputs: Motion activity heatmaps and chronological motion event spans.
Status: Stub
"""

from pathlib import Path

from app.core.models import Event


class MotionAnalyzer:
    """Analyzes motion vectors and macroblock movement (planned)."""

    def __init__(self) -> None:
        pass

    def detect_motion(self, video_path: Path | str) -> list[Event]:
        """Detect motion anomalies and export Event records.

        Raises:
            NotImplementedError: Motion vector analysis is planned.
        """
        raise NotImplementedError("planned: video stream motion vector and activity detection")
