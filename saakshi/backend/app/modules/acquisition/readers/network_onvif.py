"""Saakshi ONVIF & Network Stream Ingestion.

Purpose: Capture live network streams or replay buffers from IP cameras via ONVIF/RTSP.
Inputs: RTSP URI, ONVIF credentials, or PCAP capture files.
Outputs: Raw Annex-B NAL bitstream or MP4 segments.
Status: Stub
"""

from pathlib import Path


class NetworkStreamReader:
    """Network-level stream capture and PCAP packet extractor (planned)."""

    def __init__(self, endpoint_url: str) -> None:
        self.endpoint_url = endpoint_url

    def capture_pcap(self, pcap_path: Path | str) -> Path:
        """Parse RTP H.264 payloads from network capture.

        Raises:
            NotImplementedError: Network RTP/ONVIF parsing is planned.
        """
        raise NotImplementedError("planned: ONVIF network stream capture and RTP extraction")
