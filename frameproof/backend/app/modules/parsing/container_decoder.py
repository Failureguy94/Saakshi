"""FrameProof Container & Demuxer Engine.

Purpose: Demux proprietary surveillance video containers (e.g., DHAV, HIK-PES) into raw elementary streams.
Inputs: File or byte stream of encapsulated container.
Outputs: Extracted elementary H.264/H.265 video packets and audio tracks.
Status: Stub
"""

from pathlib import Path
from typing import BinaryIO


class ContainerDecoder:
    """Demuxer for proprietary framing wrappers (planned)."""

    def __init__(self, container_type: str) -> None:
        self.container_type = container_type

    def demux_to_annexb(self, input_file: Path | str, output_stream: BinaryIO) -> int:
        """Strip proprietary headers and emit standard Annex-B bitstream.

        Raises:
            NotImplementedError: Container demuxing is planned.
        """
        raise NotImplementedError("planned: proprietary video container demuxing to elementary stream")
