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
from saakshi.modules.custody import verify_chain

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
        print(f"[PASS] Timeline: Computed offset +{offsets[0]['offset_seconds']}s")
    except Exception as e:
        print(f"[FAIL] Timeline: {e}")
        
    try:
        events = detect_motion()
        print(f"[PASS] Analytics: Detected {events} motion events")
    except Exception as e:
        print(f"[FAIL] Analytics: {e}")
        
    try:
        pdf_path = generate_report()
        print(f"[PASS] Reporting: Report saved to {pdf_path}")
    except Exception as e:
        print(f"[FAIL] Reporting: {e}")
        
    try:
        chain_ok = verify_chain()
        if chain_ok:
            print("[PASS] Custody: Chain verified intact")
        else:
            print("[FAIL] Custody: Chain verification failed")
    except Exception as e:
        print(f"[FAIL] Custody: {e}")

if __name__ == "__main__":
    run_all()
