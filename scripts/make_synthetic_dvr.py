import os
import subprocess
import json
import struct
import random
import imageio_ffmpeg
import time

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

import cv2
import numpy as np

def generate_video(filename, text, duration=4, moving_object=False):
    fps = 25
    frames = duration * fps
    width, height = 320, 240
    
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-g", "30",
        filename
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for i in range(1, frames + 1):
        frame = np.full((height, width, 3), (255, 0, 0), dtype=np.uint8)
        
        cv2.putText(frame, str(i), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        if moving_object:
            x = 50 + int((i/fps)*60)
            y = 50
            cv2.rectangle(frame, (x, y), (x+50, y+50), (0, 0, 255), -1)
        else:
            cv2.rectangle(frame, (50, 50), (100, 100), (255, 255, 255), -1)
            
        p.stdin.write(frame.tobytes())
        
    p.stdin.close()
    p.wait()

def make_synthetic():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    random.seed(args.seed)

    os.makedirs("out", exist_ok=True)
    
    videos = []
    print("Generating H.264 clips...")
    for ch in range(1, 4):
        for seg in range(1, 5):
            fname = f"out/ch{ch}_seg{seg}.mp4"
            moving = (ch == 2 and seg == 2) or (ch == 3 and seg == 1)
            generate_video(fname, f"CH{ch}", duration=4, moving_object=moving)
            
            # Extract raw H.264 stream
            h264_name = f"out/ch{ch}_seg{seg}.h264"
            subprocess.run([ffmpeg_exe, "-y", "-i", fname, "-vcodec", "copy", "-bsf:v", "h264_mp4toannexb", "-f", "h264", h264_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            size = os.path.getsize(h264_name)
            videos.append({
                "ch": ch, "seg": seg, "file": h264_name, "size": size, "duration": 4
            })
    
    # Pick 2 segments to delete on different channels
    to_delete = []
    channels_with_deletes = set()
    shuffled_vids = list(videos)
    random.shuffle(shuffled_vids)
    for v in shuffled_vids:
        if v["ch"] not in channels_with_deletes:
            to_delete.append((v["ch"], v["seg"]))
            channels_with_deletes.add(v["ch"])
            if len(to_delete) == 2:
                break
    
    for v in videos:
        v["deleted"] = (v["ch"], v["seg"]) in to_delete

    # Construct disk image
    print("Constructing disk image...")
    disk_file = "out/synthetic_dvr.img"
    with open(disk_file, "wb") as f:
        # 1. Header (VendorX signature)
        header = b"VENDORX_DVR_V1" + b"\x00" * (512 - 14)
        f.write(header)
        
        # 2. Index Table Placeholder (512 bytes per entry)
        # We have 12 segments. Reserve 20 * 512 = 10240 bytes
        index_offset = f.tell()
        f.write(b"\x00" * 10240)
        
        # 3. Video Data
        data_offset = f.tell()
        
        index_entries = []
        ground_truth = []
        
        current_offset = data_offset
        
        # base true time
        base_time = int(time.mktime(time.strptime("2026-10-04 10:00:00", "%Y-%m-%d %H:%M:%S")))
        clock_offsets = {1: 300, 2: 298, 3: 305}
        
        for v in videos:
            true_epoch = base_time + v["seg"] * 4
            drift = v["seg"] * 0.5
            dvr_epoch = true_epoch + clock_offsets[v["ch"]] + drift
            
            # 32-byte header: magic "SEGH", channel(u16), segment(u16), camera_epoch(u64), duration(u32)
            segh = struct.pack("<4sHHQI", b"SEGH", v["ch"], v["seg"], int(true_epoch), v["duration"])
            segh += b"\x00" * (32 - len(segh))
            
            f.write(segh)
            with open(v["file"], "rb") as vf:
                data = vf.read()
                f.write(data)
            
            vid_size = len(data)
            
            # Record ground truth
            ground_truth.append({
                "channel": v["ch"],
                "segment": v["seg"],
                "offset": current_offset,
                "length": vid_size + 32, # includes header
                "deleted": v["deleted"],
                "true_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(true_epoch))
            })
            
            if not v["deleted"]:
                dvr_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(dvr_epoch)).encode('utf-8')
                # Include header length in the stored offset and length in index?
                # Usually DVR index points to the whole block or just the data. We'll point to the header.
                entry = struct.pack("<IIQ", v["ch"], v["seg"], current_offset) + struct.pack("<I", vid_size + 32) + dvr_time_str
                entry += b"\x00" * (512 - len(entry))
                index_entries.append(entry)
                
            current_offset += (vid_size + 32)
            
        # Write Index
        f.seek(index_offset)
        for entry in index_entries:
            f.write(entry)

    # Write ground truth
    with open("out/ground_truth.json", "w") as f:
        json.dump(ground_truth, f, indent=2)

    print("Done. Generated out/synthetic_dvr.img and out/ground_truth.json")

if __name__ == "__main__":
    make_synthetic()
