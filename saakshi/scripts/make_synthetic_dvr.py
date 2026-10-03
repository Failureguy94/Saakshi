import os
import struct
import subprocess
import json
import argparse
from datetime import datetime, timezone
import tempfile

def create_synthetic_dvr(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    img_path = os.path.join(output_dir, "synthetic_dvr.img")
    json_path = os.path.join(output_dir, "ground_truth.json")

    # Header parameters
    magic = b"VENDORX_DVR\x00"
    version = 1
    num_channels = 2
    clock_offset_seconds = 187
    dvr_epoch = datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp()
    
    true_start = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc).timestamp()

    # We need to generate 6 clips (3 per channel)
    # Channel 0: blue-ish background (color=blue), Channel 1: green-ish background (color=green)
    clips = []
    
    for ch in range(num_channels):
        color = "blue" if ch == 0 else "green"
        for i in range(3):
            # Clip spacing: 60 seconds
            start_offset = (ch * 3 + i) * 60
            clip_true_start = true_start + start_offset
            clip_dvr_time = clip_true_start + clock_offset_seconds
            
            # Duration 4 seconds
            duration = 4
            
            # Frame size
            width, height = 320, 240
            fps = 15
            
            has_motion = True if (i % 2 == 0) else False
            
            # Generate h264 file
            fd, tmp_path = tempfile.mkstemp(suffix=".h264")
            os.close(fd)
            
            # Use ffmpeg
            # Drawtext with actual generation time, moving rectangle if has_motion
            filter_complex = f"color=c={color}:s={width}x{height}:r={fps}:d={duration}"
            if has_motion:
                filter_complex += f",drawbox=x='t*20':y='t*20':w=50:h=50:color=white:t=fill"
            filter_complex += f",drawtext=text='CH{ch} Time %{{pts\\:hms}}':x=10:y=10:fontsize=24:fontcolor=white"

            cmd = [
                "ffmpeg", "-y", "-f", "lavfi", "-i", filter_complex,
                "-c:v", "libx264", "-preset", "ultrafast", "-bf", "0",
                "-f", "h264", tmp_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            with open(tmp_path, "rb") as f:
                data = f.read()
            os.unlink(tmp_path)
            
            clips.append({
                "channel": ch,
                "true_start_time": datetime.fromtimestamp(clip_true_start, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "dvr_timestamp": int(clip_dvr_time - dvr_epoch),
                "duration_ms": duration * 1000,
                "data": data,
                "width": width,
                "height": height,
                "fps": fps,
                "codec": 1,
                "has_motion": has_motion,
                "deleted_from_index": False
            })

    # Delete 2 index entries
    clips[1]["deleted_from_index"] = True # CH0 clip 2
    clips[4]["deleted_from_index"] = True # CH1 clip 2
    
    num_index_entries = len(clips)
    index_table_offset = 512
    data_start_offset = index_table_offset + num_index_entries * 64
    
    # Write IMG
    with open(img_path, "wb") as f:
        # Header (512 bytes)
        # magic (12), version (4), num_channels (2), num_index_entries (4), index_table_offset (8), data_start_offset (8), clock_offset_seconds (4)
        header = struct.pack("<12sIHQqqi", magic, version, num_channels, num_index_entries, index_table_offset, data_start_offset, clock_offset_seconds)
        header = header.ljust(512, b'\x00')
        f.write(header)
        
        # We will write index, then data
        # We need to compute data offsets first
        current_data_offset = data_start_offset
        for clip in clips:
            clip["offset"] = current_data_offset
            clip["length"] = len(clip["data"])
            current_data_offset += clip["length"]
            
        # Index table
        for i, clip in enumerate(clips):
            # channel_id(1), flags(1), reserved(2), start_timestamp(4), duration_ms(4), data_offset(8), data_length(8), frame_width(2), frame_height(2), fps(1), codec(1), padding(26)
            flags = 0x00 if clip["deleted_from_index"] else 0x01
            entry = struct.pack("<BBHIIQQHHBB26s", 
                clip["channel"], flags, 0, clip["dvr_timestamp"], clip["duration_ms"], 
                clip["offset"], clip["length"], clip["width"], clip["height"], 
                clip["fps"], clip["codec"], b'\x00'*26)
            f.write(entry)
            
        # Data
        for clip in clips:
            f.write(clip["data"])

    # JSON ground truth
    gt = {
        "format": "VendorX",
        "clock_offset_seconds": clock_offset_seconds,
        "dvr_epoch": "2024-01-01T00:00:00Z",
        "channels": list(range(num_channels)),
        "segments": []
    }
    
    for i, clip in enumerate(clips):
        gt["segments"].append({
            "index": i,
            "channel": clip["channel"],
            "offset": clip["offset"],
            "length": clip["length"],
            "true_start_time": clip["true_start_time"],
            "dvr_timestamp": clip["dvr_timestamp"],
            "duration_ms": clip["duration_ms"],
            "deleted_from_index": clip["deleted_from_index"],
            "has_motion": clip["has_motion"]
        })
        
    with open(json_path, "w") as f:
        json.dump(gt, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()
    create_synthetic_dvr(args.output_dir)
