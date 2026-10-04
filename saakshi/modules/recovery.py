import os
import subprocess
import hashlib
import imageio_ffmpeg
from saakshi.db import get_db
from saakshi.modules.custody import append_custody

import time
import struct
from saakshi.engine.nal_carver import default_nal_carver, group_into_gops
from saakshi.engine.gop_repair import repair_gops

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

def extract_and_carve(img_path, out_dir="out", progress_cb=None):
    os.makedirs(out_dir, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, channel, offset, length FROM segments WHERE source='indexed'")
    indexed = {row["offset"]: dict(row) for row in c.fetchall()}
    
    with open(img_path, "rb") as f:
        data = f.read()
    
    # Find all SEGH headers
    segh_sig = b"SEGH"
    idx = 0
    segments_found = []
    while idx < len(data):
        idx = data.find(segh_sig, idx)
        if idx == -1:
            break
        
        # Read header
        if idx + 32 <= len(data):
            _, ch, seg_num, camera_epoch, duration = struct.unpack("<4sHHQI", data[idx:idx+20])
            camera_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(camera_epoch))
            segments_found.append({
                "offset": idx,
                "channel": ch,
                "camera_time": camera_time
            })
        idx += 32
        
    count_indexed = 0
    carved = 0
    
    total_segs = len(segments_found)
    for i, sf in enumerate(segments_found):
        if progress_cb:
            progress_cb(i, total_segs, f"Carving segment {i}/{total_segs}")
            
        start_offset = sf["offset"]
        end_offset = segments_found[i+1]["offset"] if i + 1 < len(segments_found) else len(data)
        
        is_indexed = start_offset in indexed
        
        if is_indexed:
            # We already have offset/length from index
            idx_seg = indexed[start_offset]
            length = idx_seg["length"]
            db_id = idx_seg["id"]
            ch = idx_seg["channel"]
            prefix = f"ch{ch}_seg{db_id}_idx"
            count_indexed += 1
            source = "indexed"
        else:
            length = end_offset - start_offset
            ch = sf["channel"]
            
            c.execute("INSERT INTO segments (channel, offset, length, source, confidence, dvr_time, camera_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (ch, start_offset, length, "recovered-deleted", 0.8, sf["camera_time"], sf["camera_time"])) # use camera_time for dvr_time fallback
            db_id = c.lastrowid
            prefix = f"ch{ch}_seg{db_id}_rec"
            carved += 1
            source = "recovered-deleted"
            
        raw_path = f"{out_dir}/{prefix}.h264"
        with open(raw_path, "wb") as rf:
            rf.write(data[start_offset+32:start_offset+length])
            
        mp4_path = f"{out_dir}/{prefix}.mp4"
        subprocess.run([ffmpeg_exe, "-y", "-i", raw_path, "-c", "copy", mp4_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        with open(mp4_path, "rb") as mf:
            file_hash = hashlib.sha256(mf.read()).hexdigest()
            
        c.execute("UPDATE segments SET file_path=?, file_hash=? WHERE id=?", (mp4_path, file_hash, db_id))
        
    conn.commit()
    conn.close()
    
    if progress_cb:
        progress_cb(total_segs, total_segs, "Carving complete")
        
    append_custody("Recovery", f"Recovered {count_indexed} indexed, {carved} deleted segments")
    return count_indexed, carved

if __name__ == "__main__":
    import sys
    print(extract_and_carve(sys.argv[1]))
