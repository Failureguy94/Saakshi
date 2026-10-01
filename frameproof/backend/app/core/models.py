"""FrameProof Unified Evidence Model (UEM).

Purpose: Vendor-agnostic domain models for digital video forensic evidence.
Inputs: Normalized forensic metadata.
Outputs: Validated domain objects (Device, EvidenceImage, Volume, Channel, Segment, Frame, Event, TimeAnchor).
Status: Implemented
"""

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class FrameType(StrEnum):
    """Classification of video frames."""

    I_FRAME = "I_FRAME"
    P_FRAME = "P_FRAME"
    B_FRAME = "B_FRAME"
    UNKNOWN = "UNKNOWN"


class EventType(StrEnum):
    """Classification of forensic detected events."""

    MOTION = "MOTION"
    TAMPER = "TAMPER"
    FACE_DETECTED = "FACE_DETECTED"
    OBJECT_TRACK = "OBJECT_TRACK"
    SYSTEM_REBOOT = "SYSTEM_REBOOT"


class TimeAnchor(BaseModel):
    """Triangulated forensic timestamp reconciling RTC, OSD OCR, and video headers."""

    id: str = Field(description="Unique anchor identifier")
    frame_id: str = Field(description="Associated frame ID")
    rtc_timestamp: datetime | None = Field(default=None, description="Reported internal RTC time")
    osd_timestamp: datetime | None = Field(default=None, description="Visual OCR extracted timestamp")
    header_pts: int | None = Field(default=None, description="Presentation Timestamp clock from stream")
    reconciled_utc: datetime = Field(description="Reconciled true UTC forensic timestamp")
    trust_score: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")


class Event(BaseModel):
    """Forensic occurrence or anomaly in recovered footage."""

    id: str = Field(description="Unique event ID")
    segment_id: str = Field(description="Associated segment ID")
    event_type: EventType = Field(description="Category of detected event")
    start_frame_id: str = Field(description="Starting frame identifier")
    end_frame_id: str = Field(description="Ending frame identifier")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence metric")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary event attributes")


class Frame(BaseModel):
    """Atomic video presentation unit or NAL slice."""

    id: str = Field(description="Unique frame ID")
    segment_id: str = Field(description="Host segment ID")
    frame_index: int = Field(ge=0, description="Index within segment")
    frame_type: FrameType = Field(default=FrameType.UNKNOWN, description="Frame slice type")
    stream_offset: int = Field(ge=0, description="Byte offset in source image/container")
    size_bytes: int = Field(gt=0, description="Byte size of frame data")
    sha256_hash: str = Field(description="SHA-256 cryptographic digest of frame bytes")
    pts: int | None = Field(default=None, description="Presentation Timestamp")
    dts: int | None = Field(default=None, description="Decoding Timestamp")


class Segment(BaseModel):
    """Contiguous video sequence recovered from index or carving."""

    id: str = Field(description="Unique segment ID")
    channel_id: str = Field(description="Camera channel ID")
    start_time: datetime = Field(description="Estimated start time UTC")
    end_time: datetime = Field(description="Estimated end time UTC")
    codec: Literal["H264", "H265", "MPEG4", "UNKNOWN"] = Field(default="H264")
    frame_count: int = Field(default=0, ge=0)
    merkle_root: str | None = Field(default=None, description="Merkle root of frame hashes")
    is_carved: bool = Field(default=False, description="True if recovered from unallocated slack")


class Channel(BaseModel):
    """Camera video feed from DVR/NVR."""

    id: str = Field(description="Unique channel ID")
    volume_id: str = Field(description="Host storage volume ID")
    channel_number: int = Field(ge=1, description="Physical DVR port/camera number")
    camera_name: str = Field(default="Camera", description="Label from OSD or configuration")
    resolution_width: int = Field(default=1920, ge=0)
    resolution_height: int = Field(default=1080, ge=0)
    frame_rate: float = Field(default=25.0, ge=0.0)


class Volume(BaseModel):
    """Partition or logical container carved from evidence image."""

    id: str = Field(description="Unique volume ID")
    evidence_image_id: str = Field(description="Source evidence image ID")
    volume_index: int = Field(ge=0, description="Partition index")
    start_sector: int = Field(ge=0, description="Sector offset on disk")
    sector_count: int = Field(gt=0, description="Total sectors in volume")
    filesystem_type: str = Field(description="Detected filesystem or RAW_CARVE")


class EvidenceImage(BaseModel):
    """Bit-stream physical disk image under forensic analysis."""

    id: str = Field(description="Unique image ID")
    device_id: str = Field(description="Parent hardware device ID")
    filename: str = Field(description="File name of image")
    source_path: str = Field(description="Path to read-only evidence file")
    format: Literal["RAW_DD", "E01", "AFF4", "IMAGE"] = Field(default="RAW_DD")
    size_bytes: int = Field(ge=0, description="Exact size in bytes")
    md5_hash: str = Field(description="Intake MD5 checksum")
    sha256_hash: str = Field(description="Intake SHA-256 checksum")
    acquired_at: datetime = Field(default_factory=datetime.utcnow)
    acquired_by: str = Field(description="Investigator badge or identifier")


class Device(BaseModel):
    """Physical DVR/NVR unit seized as digital evidence."""

    id: str = Field(description="Unique device ID")
    case_id: str = Field(description="Associated forensic case ID")
    make: str = Field(default="Unknown", description="OEM manufacturer")
    model: str = Field(default="Unknown", description="Model identifier")
    serial_number: str = Field(default="Unknown", description="Hardware serial number")
    mac_address: str | None = Field(default=None, description="Primary MAC address")
    rtc_offset_seconds: float = Field(default=0.0, description="Clock drift offset")
