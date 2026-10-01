# Saakshi Unified Evidence Model (UEM) Specification

The Unified Evidence Model (UEM) provides a vendor-agnostic, hierarchical abstraction for digital surveillance evidence. Regardless of whether source footage is extracted from Dahua DHFS, Hikvision HIKFS, generic FAT/ext4 partitions, or carved unallocated slack sectors, Saakshi standardizes all artifacts into a cohesive data model.

---

## 1. Hierarchy Overview

```text
Case
 └── Device (Physical DVR/NVR unit, MAC, serial number, make/model)
      └── EvidenceImage (Bit-stream copy, E01, Raw DD, MD5/SHA256 digests)
           └── Volume (Partition or logical storage pool on image)
                └── Channel (Surveillance camera stream, camera name, resolution)
                     └── Segment (Contiguous video clip, start/end timestamps, codec)
                          └── Frame (Individual I/P/B frame or NAL unit, offset, hash)
                               ├── Event (Motion trigger, tamper alert, object detected)
                               └── TimeAnchor (Cross-validated timestamp: RTC vs Header vs OSD)
```

---

## 2. Entity Specifications

### 2.1 Device
Represents the seized physical hardware or appliance.
- `id`: Unique identifier (UUIDv4).
- `case_id`: Associated forensic case.
- `make`: OEM Manufacturer (or "Unknown").
- `model`: Device model identifier.
- `serial_number`: Hardware serial number.
- `mac_address`: Network interface MAC address.
- `rtc_offset_seconds`: Quantified internal clock drift against UTC.

### 2.2 EvidenceImage
A cryptographic bit-stream image acquired from physical media.
- `id`: Unique identifier (UUIDv4).
- `device_id`: Associated Device.
- `filename`: Image filename.
- `source_path`: Absolute path on write-blocked evidence mount.
- `format`: Raw DD, EnCase E01, or AFF4.
- `size_bytes`: Total byte length.
- `md5_hash`: Hexadecimal MD5 digest computed at acquisition.
- `sha256_hash`: Hexadecimal SHA-256 digest computed at acquisition.
- `acquired_at`: UTC timestamp of acquisition.
- `acquired_by`: Forensic examiner identifier.

### 2.3 Volume
A logical storage volume, proprietary partition, or carving pool.
- `id`: Unique identifier (UUIDv4).
- `evidence_image_id`: Host evidence image.
- `volume_index`: Zero-based volume index.
- `start_sector`: Starting sector offset on physical image.
- `sector_count`: Total sectors in volume.
- `filesystem_type`: Detected filesystem (e.g., `DHFS4.1`, `HIKFS2.0`, `RAW_CARVE`).

### 2.4 Channel
A specific camera input or recording feed.
- `id`: Unique identifier (UUIDv4).
- `volume_id`: Associated volume.
- `channel_number`: DVR channel number (e.g. Channel 1, Camera 04).
- `camera_name`: Label extracted from OSD or DVR metadata.
- `resolution_width`: Video horizontal pixel count.
- `resolution_height`: Video vertical pixel count.
- `frame_rate`: Average frames per second.

### 2.5 Segment
A contiguous sequence of video frames between start and end timestamps.
- `id`: Unique identifier (UUIDv4).
- `channel_id`: Associated camera channel.
- `start_time`: Extracted start timestamp (UTC).
- `end_time`: Extracted end timestamp (UTC).
- `codec`: Video compression standard (`H264`, `H265`, `MPEG4`).
- `frame_count`: Number of indexed frames.
- `merkle_root`: Root hash of the Merkle tree over segment frames.
- `is_carved`: Boolean indicating if recovered from unallocated/slack space.

### 2.6 Frame
An atomic presentation unit or NAL slice.
- `id`: Unique identifier (UUIDv4).
- `segment_id`: Host segment.
- `frame_index`: Sequence position within segment.
- `frame_type`: Frame classification (`I_FRAME`, `P_FRAME`, `B_FRAME`, `UNKNOWN`).
- `stream_offset`: Byte offset within the container or raw image.
- `size_bytes`: Byte length of frame data.
- `sha256_hash`: Frame cryptographic digest.
- `pts`: Presentation Timestamp.
- `dts`: Decoding Timestamp.

### 2.7 Event
A temporally bounded occurrence identified within footage.
- `id`: Unique identifier (UUIDv4).
- `segment_id`: Associated segment.
- `event_type`: Event category (`MOTION`, `TAMPER`, `FACE_DETECTED`, `OBJECT_TRACK`).
- `start_frame_id`: Initial frame index.
- `end_frame_id`: Concluding frame index.
- `confidence`: Confidence score (0.0 to 1.0).
- `metadata`: Key-value attributes.

### 2.8 TimeAnchor
Forensic timestamp triangulation reconciling device clock, stream headers, and visual OSD.
- `id`: Unique identifier (UUIDv4).
- `frame_id`: Associated frame.
- `rtc_timestamp`: Recorded system timestamp from metadata.
- `osd_timestamp`: Timestamp extracted via OCR from visible on-screen display.
- `header_pts`: Clock derived from container presentation timestamp.
- `reconciled_utc`: Forensic best-estimate true UTC timestamp.
- `trust_score`: Calculated confidence metric (0.0 to 1.0).
