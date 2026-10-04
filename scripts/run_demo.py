import os
import sys

# Ensure imports work from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from saakshi.db import init_db
from scripts.make_synthetic_dvr import make_synthetic
from saakshi.modules.identification import identify_image
from saakshi.modules.acquisition import acquire_image
from saakshi.modules.parsing import parse_vendorx
from saakshi.modules.recovery import extract_and_carve
from saakshi.modules.timeline import analyze_timeline
from saakshi.modules.analytics import detect_motion
from saakshi.modules.reporting import generate_report
from saakshi.modules.custody import verify_chain, create_manifest, tamper_clip_copy, verify_manifest, restore_clip_copy

def run_all():
    print("Initializing Database...")
    if os.path.exists("out/saakshi.db"):
        os.remove("out/saakshi.db")
    init_db()
    
    print("\n--- Generating Synthetic Data ---")
    make_synthetic()
    
    img_path = "out/synthetic_dvr.img"
    
    print("\n--- Pipeline Stages ---")
    
    try:
        match, conf = identify_image(img_path)
        print(f"[PASS] Identification: {match} ({conf})")
    except Exception as e:
        print(f"[FAIL] Identification: {e}")
        
    try:
        hashes = acquire_image(img_path)
        print(f"[PASS] Acquisition: SHA256={hashes['sha256'][:8]}...")
    except Exception as e:
        print(f"[FAIL] Acquisition: {e}")
        
    try:
        c = parse_vendorx(img_path)
        print(f"[PASS] Parsing: {c} indexed segments found")
    except Exception as e:
        print(f"[FAIL] Parsing: {e}")
        
    try:
        i, d = extract_and_carve(img_path)
        print(f"[PASS] Recovery: {i} indexed, {d} carved segments extracted")
    except Exception as e:
        print(f"[FAIL] Recovery: {e}")
        
    try:
        offsets = analyze_timeline()
        first_ch = list(offsets['channels'].keys())[0]
        off_sec = offsets['channels'][first_ch]['offset_seconds']
        print(f"[PASS] Timeline: Computed offset +{off_sec}s")
    except Exception as e:
        print(f"[FAIL] Timeline: {e}")
        
    try:
        events = detect_motion()
        print(f"[PASS] Analytics: Detected {events} motion events")
    except Exception as e:
        print(f"[FAIL] Analytics: {e}")
        
    try:
        chain_ok, err_idx = verify_chain()
        if chain_ok:
            print("[PASS] Custody: Chain verified intact")
        else:
            print(f"[FAIL] Custody: Chain verification failed at index {err_idx}")
            
        root = create_manifest(img_path)
        print(f"[PASS] Custody: Merkle root {root}")
        
        tampered_path = tamper_clip_copy(1)
        if tampered_path:
            ok, path, exp, act = verify_manifest()
            if not ok:
                print(f"[PASS] Custody: Tamper detected in {path}")
            else:
                print(f"[FAIL] Custody: Tamper NOT detected")
            restore_clip_copy(1)
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"[FAIL] Custody: {e}")
        
    try:
        pdf_path = generate_report()
        print(f"[PASS] Reporting: Report saved to {pdf_path}")
    except Exception as e:
        print(f"[FAIL] Reporting: {e}")

if __name__ == "__main__":
    run_all()
