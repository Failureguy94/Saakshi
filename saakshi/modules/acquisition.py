import hashlib
from saakshi.modules.custody import append_custody

def acquire_image(img_path):
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    
    with open(img_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
            sha256.update(chunk)
            
    res = {
        "md5": md5.hexdigest(),
        "sha256": sha256.hexdigest()
    }
    append_custody("Acquisition", f"Acquired {img_path}", data_hash=res["sha256"])
    return res

if __name__ == "__main__":
    import sys
    print(acquire_image(sys.argv[1]))
