import os
import subprocess
import hashlib
import imageio_ffmpeg
from saakshi.db import get_db
from saakshi.modules.custody import append_custody

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

def extract_and_carve(img_path, out_dir="out"):
    os.makedirs(out_dir, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM segments")
    indexed = c.fetchall()
    
    # 1. Extract Indexed
    count_indexed = 0
    with open(img_path, "rb") as f:
        for seg in indexed:
            f.seek(seg["offset"])
            data = f.read(seg["length"])
            raw_path = f"{out_dir}/ch{seg['channel']}_seg{seg['id']}_idx.h264"
            with open(raw_path, "wb") as rf:
                rf.write(data)
            
            mp4_path = f"{out_dir}/ch{seg['channel']}_seg{seg['id']}_idx.mp4"
            subprocess.run([ffmpeg_exe, "-y", "-i", raw_path, "-c", "copy", mp4_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            with open(mp4_path, "rb") as mf:
                file_hash = hashlib.sha256(mf.read()).hexdigest()
                
            c.execute("UPDATE segments SET file_path=?, file_hash=? WHERE id=?", (mp4_path, file_hash, seg["id"]))
            count_indexed += 1
            
    # 2. Carve Unindexed (naive NAL carving for this demo)
    # The index used 5120 bytes for index table, starting at 512.
    # Video data starts at 5632.
    c.execute("SELECT offset, length FROM segments ORDER BY offset")
    known_regions = []
    for row in c.fetchall():
        known_regions.append((row["offset"], row["offset"] + row["length"]))
        
    def is_unallocated(offset):
        for start, end in known_regions:
            if start <= offset < end:
                return False
        return True

    carved = 0
    with open(img_path, "rb") as f:
        f.seek(5632)
        data = f.read()
    
    # Very simple carving: look for NAL 00 00 00 01
    nal_sig = b'\x00\x00\x00\x01'
    idx = 0
    while idx < len(data):
        idx = data.find(nal_sig, idx)
        if idx == -1:
            break
        
        abs_offset = 5632 + idx
        if is_unallocated(abs_offset):
            # Found start of a deleted segment
            # Find next large block of unallocated NALs, or just grab a chunk for demo
            # In our synthetic data, segments are contiguous.
            # Let's find where this unallocated block ends.
            end_idx = len(data)
            for start, end in known_regions:
                if start > abs_offset:
                    end_idx = min(end_idx, start - 5632)
            
            seg_data = data[idx:end_idx]
            
            if len(seg_data) > 500: # reasonably large to be video
                # Save it
                carved += 1
                c.execute("INSERT INTO segments (channel, offset, length, is_recovered, confidence) VALUES (?, ?, ?, ?, ?)",
                          (0, abs_offset, len(seg_data), True, 0.8))
                seg_id = c.lastrowid
                
                raw_path = f"{out_dir}/recovered_seg{seg_id}.h264"
                with open(raw_path, "wb") as rf:
                    rf.write(seg_data)
                
                mp4_path = f"{out_dir}/recovered_seg{seg_id}.mp4"
                subprocess.run([ffmpeg_exe, "-y", "-i", raw_path, "-c", "copy", mp4_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                with open(mp4_path, "rb") as mf:
                    file_hash = hashlib.sha256(mf.read()).hexdigest()
                    
                c.execute("UPDATE segments SET file_path=?, file_hash=? WHERE id=?", (mp4_path, file_hash, seg_id))
            
            idx = end_idx
        else:
            idx += 1

    conn.commit()
    conn.close()
    
    append_custody("Recovery", f"Recovered {count_indexed} indexed, {carved} deleted segments")
    return count_indexed, carved

if __name__ == "__main__":
    import sys
    print(extract_and_carve(sys.argv[1]))
