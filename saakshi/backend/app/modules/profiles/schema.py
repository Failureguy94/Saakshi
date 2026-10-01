"""Saakshi OEM Vendor Profile Schema.

Purpose: Formal Pydantic specification for DVR/NVR proprietary storage profiles.
Inputs: Raw dictionary / YAML deserialized structures.
Outputs: Strongly typed, validated VendorProfile instances.
Status: Implemented
"""

from typing import Literal

from pydantic import BaseModel, Field


class SignatureRule(BaseModel):
    """Rule for identifying filesystem or container signatures."""

    name: str = Field(description="Name or descriptor of signature")
    offset: int | None = Field(default=None, description="Byte offset from partition start or sector")
    magic_hex: str | None = Field(default=None, description="Hex-encoded byte signature")
    regex: str | None = Field(default=None, description="Regular expression pattern")
    description: str = Field(default="", description="Technical rationale")


class VolumeLayout(BaseModel):
    """Specification of disk volume, sector geometry, and superblocks."""

    sector_size_bytes: int = Field(default=512, ge=512)
    cluster_size_bytes: int | None = Field(default=None)
    superblock_offset: int | None = Field(default=None)
    partition_scheme: str = Field(default="TODO", description="Partitioning scheme")


class IndexStructure(BaseModel):
    """Metadata indexing layout for recording catalog."""

    index_type: str = Field(default="TODO", description="Table of contents structure")
    entry_size_bytes: int | None = Field(default=None)
    timestamp_encoding: str = Field(default="TODO", description="Binary timestamp packing scheme")
    channel_map_strategy: str = Field(default="TODO", description="Camera channel mapping logic")


class ContainerType(BaseModel):
    """Framing and container encapsulation format."""

    stream_format: str = Field(default="TODO", description="Container or stream type")
    frame_header_magic: str | None = Field(default=None, description="Per-frame header magic bytes")


class TimestampSpec(BaseModel):
    """Clock, epoch, and resolution definitions."""

    epoch_format: str = Field(default="TODO", description="Epoch representation")
    resolution: str = Field(default="TODO", description="Precision (seconds, milliseconds, ticks)")
    timezone_assumption: str = Field(default="UTC", description="Default timezone behavior")


class VendorProfile(BaseModel):
    """Complete OEM DVR/NVR forensic profile specification."""

    vendor_id: str = Field(description="Unique normalized vendor slug")
    vendor_name: str = Field(description="Commercial OEM display name")
    status: Literal["placeholder", "draft", "verified", "production"] = Field(
        default="placeholder",
        description="Forensic readiness tier",
    )
    supported_models: list[str] = Field(default_factory=list)
    firmware_versions: list[str] = Field(default_factory=list)
    identification_signatures: list[SignatureRule] = Field(default_factory=list)
    volume_layout: VolumeLayout = Field(default_factory=VolumeLayout)
    index_structure: IndexStructure = Field(default_factory=IndexStructure)
    container_type: ContainerType = Field(default_factory=ContainerType)
    timestamp_fields: TimestampSpec = Field(default_factory=TimestampSpec)
    notes: str = Field(default="")
    todo_fields: list[str] = Field(default_factory=list)
