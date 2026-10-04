import struct
from saakshi.db import get_db
from saakshi.modules.custody import append_custody

def parse_vendorx(img_path):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM segments")
    
    with open(img_path, "rb") as f:
        # Skip header
        f.seek(512)
        
        # Read index table (10240 bytes max, 512 per entry)
        index_data = f.read(10240)
        
    count = 0
    for i in range(0, len(index_data), 512):
        entry = index_data[i:i+512]
        if entry.startswith(b'\x00\x00\x00\x00'): # Empty
            continue
            
        try:
            channel, segment, offset, length = struct.unpack("<IIQI", entry[:20])
            if channel == 0:
                continue
            dvr_time = entry[20:].decode('utf-8', errors='ignore').strip('\x00')
            
            with open(img_path, "rb") as mf:
                mf.seek(offset)
                segh_data = mf.read(32)
                if segh_data.startswith(b"SEGH"):
                    _, _, _, camera_epoch, _ = struct.unpack("<4sHHQI", segh_data[:20])
                    import time
                    camera_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(camera_epoch))
                else:
                    camera_time = dvr_time
            
            c.execute(
                "INSERT INTO segments (channel, offset, length, source, confidence, dvr_time, camera_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (channel, offset, length, "indexed", 1.0, dvr_time, camera_time)
            )
            count += 1
        except Exception as e:
            print("Parse error:", e)
            
    conn.commit()
    conn.close()
    append_custody("Parsing", f"Parsed {count} indexed segments from {img_path}")
    return count

if __name__ == "__main__":
    import sys
    print(parse_vendorx(sys.argv[1]))
