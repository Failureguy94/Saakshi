import hashlib
from saakshi.db import get_db

def append_custody(stage, description, data_hash=""):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT data_hash FROM custody_log ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    prev_hash = row["data_hash"] if row else "GENESIS"
    
    # Simple hash chain
    chain_data = f"{prev_hash}|{stage}|{description}|{data_hash}".encode('utf-8')
    current_hash = hashlib.sha256(chain_data).hexdigest()
    
    c.execute(
        "INSERT INTO custody_log (stage, description, data_hash, prev_hash) VALUES (?, ?, ?, ?)",
        (stage, description, current_hash, prev_hash)
    )
    conn.commit()
    conn.close()
    return current_hash

def compute_merkle_root():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT data_hash FROM custody_log ORDER BY id ASC")
    hashes = [row["data_hash"] for row in c.fetchall()]
    conn.close()
    
    if not hashes:
        return ""
    
    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])
        new_hashes = []
        for i in range(0, len(hashes), 2):
            combined = f"{hashes[i]}{hashes[i+1]}".encode('utf-8')
            new_hashes.append(hashlib.sha256(combined).hexdigest())
        hashes = new_hashes
    return hashes[0]

def verify_chain():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM custody_log ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return True
        
    prev = "GENESIS"
    for row in rows:
        if row["prev_hash"] != prev:
            return False
        prev = row["data_hash"]
    return True
