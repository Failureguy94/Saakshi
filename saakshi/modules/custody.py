import hashlib
import json
import os
import shutil
import datetime
from saakshi.db import get_db
from saakshi.backend.app.modules.custody.chain import compute_entry_hash
from saakshi.backend.app.modules.custody.merkle import MerkleTree, ProofStep

def append_custody(stage, description, data_hash=""):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, entry_hash FROM custody_log ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    prev_hash = row["entry_hash"] if row else ("0" * 64)
    idx = row["id"] + 1 if row else 0
    
    ts = datetime.datetime.utcnow().isoformat()
    
    current_hash = compute_entry_hash(
        index=idx,
        timestamp=ts,
        actor="demo_system",
        action=stage,
        evidence_id="img1",
        evidence_hash=data_hash,
        previous_hash=prev_hash,
        details={"description": description}
    )
    
    c.execute(
        "INSERT INTO custody_log (id, timestamp, stage, description, evidence_hash, entry_hash, prev_hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (idx, ts, stage, description, data_hash, current_hash, prev_hash)
    )
    conn.commit()
    conn.close()
    return current_hash

def verify_chain():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM custody_log ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return True, -1
        
    prev = "0" * 64
    for row in rows:
        if row["prev_hash"] != prev:
            return False, row["id"]
            
        expected = compute_entry_hash(
            index=row["id"],
            timestamp=row["timestamp"],
            actor="demo_system",
            action=row["stage"],
            evidence_id="img1",
            evidence_hash=row["evidence_hash"],
            previous_hash=row["prev_hash"],
            details={"description": row["description"]}
        )
        if row["entry_hash"] != expected:
            return False, row["id"]
        prev = row["entry_hash"]
        
    return True, -1

def create_manifest(img_path):
    with open(img_path, "rb") as f:
        img_hash = hashlib.sha256(f.read()).hexdigest()
        
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, file_path, file_hash FROM segments WHERE file_path IS NOT NULL ORDER BY id")
    clips = c.fetchall()
    conn.close()
    
    hashes = [r["file_hash"] for r in clips]
    hashes.append(img_hash)
    
    tree = MerkleTree(hashes)
    
    manifest = {
        "image_hash": img_hash,
        "merkle_root": tree.root,
        "clips": {r["file_path"]: r["file_hash"] for r in clips}
    }
    with open("out/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    return tree.root

def get_all_clip_hashes(img_path):
    with open(img_path, "rb") as f:
        img_hash = hashlib.sha256(f.read()).hexdigest()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT file_hash FROM segments WHERE file_hash IS NOT NULL ORDER BY id")
    hashes = [r["file_hash"] for r in c.fetchall()]
    conn.close()
    hashes.append(img_hash)
    return hashes

def merkle_proof(clip_hash, img_path):
    hashes = get_all_clip_hashes(img_path)
    tree = MerkleTree(hashes)
    if clip_hash in hashes:
        idx = hashes.index(clip_hash)
        return tree.get_proof(idx)
    return None

def verify_proof(leaf_hash, proof, root):
    return MerkleTree.verify_proof(leaf_hash, proof, root)

def tamper_clip_copy(clip_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT file_path FROM segments WHERE id=?", (clip_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        orig = row["file_path"]
        os.makedirs("out/tamper", exist_ok=True)
        backup_path = f"out/tamper/backup_{os.path.basename(orig)}"
        shutil.copy2(orig, backup_path)
        
        with open(orig, "r+b") as f:
            f.seek(100)
            b = f.read(1)
            f.seek(100)
            f.write(bytes([b[0] ^ 0xFF]))
        return orig
    return None

def restore_clip_copy(clip_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT file_path FROM segments WHERE id=?", (clip_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        orig = row["file_path"]
        backup_path = f"out/tamper/backup_{os.path.basename(orig)}"
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, orig)

def verify_manifest():
    if not os.path.exists("out/manifest.json"):
        return True, None, None, None
    with open("out/manifest.json", "r") as f:
        manifest = json.load(f)
        
    for path, expected_hash in manifest["clips"].items():
        if not os.path.exists(path):
            return False, path, expected_hash, "MISSING"
        with open(path, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        if actual != expected_hash:
            return False, path, expected_hash, actual
            
    return True, None, None, None
