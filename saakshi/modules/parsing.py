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
        
        # Read index table (5120 bytes max, 512 per entry)
        index_data = f.read(5120)
        
    count = 0
    for i in range(0, len(index_data), 512):
        entry = index_data[i:i+512]
        if entry.startswith(b'\x00\x00\x00\x00'): # Empty
            continue
            
        try:
            channel, segment, offset, length = struct.unpack("<IIQI", entry[:20])
            if channel == 0:
                continue
            timestamp = entry[20:].decode('utf-8', errors='ignore').strip('\x00')
            
            c.execute(
                "INSERT INTO segments (channel, offset, length, timestamp, is_recovered, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                (channel, offset, length, timestamp, False, 1.0)
            )
            count += 1
        except Exception:
            pass
            
    conn.commit()
    conn.close()
    append_custody("Parsing", f"Parsed {count} indexed segments from {img_path}")
    return count

if __name__ == "__main__":
    import sys
    print(parse_vendorx(sys.argv[1]))
