import glob
import yaml
from saakshi.modules.custody import append_custody

def identify_image(img_path):
    with open(img_path, "rb") as f:
        header = f.read(512).decode('utf-8', errors='ignore').strip('\x00')
    
    profiles = glob.glob("profiles/*.yaml")
    best_match = "Unknown"
    confidence = 0.0
    
    for p in profiles:
        with open(p, "r") as pf:
            prof = yaml.safe_load(pf)
        if "signature" in prof and prof["signature"]:
            if header.startswith(prof["signature"]):
                best_match = prof["name"]
                confidence = 1.0
                break
    
    append_custody("Identification", f"Matched profile {best_match} with confidence {confidence}")
    return best_match, confidence

if __name__ == "__main__":
    import sys
    print(identify_image(sys.argv[1]))
