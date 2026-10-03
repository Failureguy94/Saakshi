import os
import subprocess
import json
import struct
import random
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

def generate_video(filename, text, duration=5, moving_object=False):
    # Base command
    cmd = [
        ffmpeg_exe, "-y", "-f", "lavfi", "-i", f"color=c=blue:s=320x240:d={duration}",
    ]
    
    if moving_object:
        # A simple moving box
        vf = "drawbox=x='50+t*20':y=50:w=50:h=50:color=red@0.8:t=fill"
    else:
        # Static box just to have something
        vf = "drawbox=x=50:y=50:w=50:h=50:color=white@0.5:t=fill"

    cmd.extend(["-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-g", "30", filename])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def make_synthetic():
    os.makedirs("out", exist_ok=True)
    
    # 3 channels, 3 segments each
    # Channel 1: static
    # Channel 2: moving object in seg 2
    # Channel 3: static
    
    videos = []
    print("Generating H.264 clips...")
    for ch in range(1, 4):
        for seg in range(1, 4):
            fname = f"out/ch{ch}_seg{seg}.mp4"
            moving = (ch == 2 and seg == 2)
            generate_video(fname, f"CH{ch}", duration=3, moving_object=moving)
            
            # Extract raw H.264 stream
            h264_name = f"out/ch{ch}_seg{seg}.h264"
            subprocess.run([ffmpeg_exe, "-y", "-i", fname, "-vcodec", "copy", "-bsf:v", "h264_mp4toannexb", "-f", "h264", h264_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            size = os.path.getsize(h264_name)
            videos.append({
                "ch": ch, "seg": seg, "file": h264_name, "size": size, "deleted": (ch == 1 and seg == 2)
            })

    # Construct disk image
    print("Constructing disk image...")
    disk_file = "out/synthetic_dvr.img"
    with open(disk_file, "wb") as f:
        # 1. Header (VendorX signature)
        header = b"VENDORX_DVR_V1" + b"\x00" * (512 - 14)
        f.write(header)
        
        # 2. Index Table Placeholder (512 bytes per entry)
        # We have 9 segments, so 9 * 512 = 4608 bytes. Let's reserve 10 * 512 = 5120 bytes
        index_offset = f.tell()
        f.write(b"\x00" * 5120)
        
        # 3. Video Data
        data_offset = f.tell()
        
        index_entries = []
        ground_truth = []
        
        current_offset = data_offset
        for v in videos:
            with open(v["file"], "rb") as vf:
                data = vf.read()
                f.write(data)
            
            # Record ground truth
            ground_truth.append({
                "channel": v["ch"],
                "segment": v["seg"],
                "offset": current_offset,
                "length": v["size"],
                "deleted": v["deleted"],
                "true_time": f"2026-10-04 10:00:{v['seg']*3:02d}"
            })
            
            if not v["deleted"]:
                # DVR clock is 5 minutes ahead
                dvr_time = f"2026-10-04 10:05:{v['seg']*3:02d}".encode('utf-8')
                entry = struct.pack("<IIQ", v["ch"], v["seg"], current_offset) + struct.pack("<I", v["size"]) + dvr_time
                entry += b"\x00" * (512 - len(entry))
                index_entries.append(entry)
                
            current_offset += v["size"]
            
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
