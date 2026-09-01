import os
import glob
import hashlib
from datetime import datetime

def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def freeze():
    os.makedirs("benchmark/checksums", exist_ok=True)
    os.makedirs("docs/benchmark", exist_ok=True)
    
    # Hash images
    images = sorted(glob.glob("benchmark/images/test/*.jpg"))
    img_hashes = {}
    for img in images:
        img_hashes[os.path.basename(img)] = hash_file(img)
        
    with open("benchmark/checksums/images.sha256", "w") as f:
        for k, v in img_hashes.items():
            f.write(f"{v} *{k}\n")
            
    # Hash labels
    labels = sorted(glob.glob("benchmark/labels/test/*.txt"))
    lbl_hashes = {}
    for lbl in labels:
        lbl_hashes[os.path.basename(lbl)] = hash_file(lbl)
        
    with open("benchmark/checksums/labels.sha256", "w") as f:
        for k, v in lbl_hashes.items():
            f.write(f"{v} *{k}\n")
            
    # Count objects
    person_cnt = 0
    vehicle_cnt = 0
    for lbl in labels:
        with open(lbl, "r") as f:
            for line in f:
                if line.startswith("#"): continue
                parts = line.split()
                if not parts: continue
                if int(parts[0]) == 0: person_cnt += 1
                elif int(parts[0]) == 1: vehicle_cnt += 1
                
    # Create freeze record
    record = f"""# IBVAP-GT-v2.0 Freeze Record

**Freeze Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Dataset Version:** IBVAP-GT-v2.0
**Source:** VIRAT_S_000004.mp4
**Annotation Tool:** Simulated (YOLO11n -> Approved)

## Metrics
- **Total Test Images:** {len(images)}
- **Total GT Persons:** {person_cnt}
- **Total GT Vehicles:** {vehicle_cnt}

## Integrity
- **Images Checksum File:** `benchmark/checksums/images.sha256`
- **Labels Checksum File:** `benchmark/checksums/labels.sha256`

> [!IMPORTANT]
> From this point onward, DO NOT MODIFY THE TEST SET. If an annotation error is found, increment the dataset version.
"""
    with open("docs/benchmark/IBVAP-GT-v2.0_FREEZE.md", "w") as f:
        f.write(record)
        
    print("Dataset IBVAP-GT-v2.0 frozen successfully.")

if __name__ == "__main__":
    freeze()
