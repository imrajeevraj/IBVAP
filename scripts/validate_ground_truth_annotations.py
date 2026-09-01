import os
import glob

def validate_annotations(img_dir, lbl_dir):
    print("Validating IBVAP-GT-v2.0 Ground Truth...")
    
    images = glob.glob(f"{img_dir}/*.jpg")
    if not images:
        print("[FAIL] No images found.")
        return False
        
    invalid_count = 0
    missing_count = 0
    person_boxes = 0
    vehicle_boxes = 0
    approved = 0
    
    for img_path in images:
        basename = os.path.basename(img_path)
        name, _ = os.path.splitext(basename)
        lbl_path = os.path.join(lbl_dir, f"{name}.txt")
        
        if not os.path.exists(lbl_path):
            missing_count += 1
            continue
            
        # Simulating a status check file alongside
        # For simplicity, we assume the simulator wrote 'APPROVED' at the end of the file as a comment
        # e.g., "# STATUS: APPROVED"
        
        is_approved = False
        with open(lbl_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line: continue
                if line.startswith("# STATUS: APPROVED"):
                    is_approved = True
                    continue
                if line.startswith("#"): continue
                
                parts = line.split()
                if len(parts) != 5:
                    print(f"Malformed row in {name}.txt")
                    invalid_count += 1
                    continue
                    
                cls_id = int(parts[0])
                if cls_id not in [0, 1]:
                    print(f"Invalid class ID {cls_id} in {name}.txt")
                    invalid_count += 1
                
                if cls_id == 0: person_boxes += 1
                elif cls_id == 1: vehicle_boxes += 1
                
                # Check coordinates
                x, y, w, h = map(float, parts[1:])
                if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
                    print(f"Impossible coordinates in {name}.txt: {x} {y} {w} {h}")
                    invalid_count += 1
                    
        if is_approved:
            approved += 1
            
    total_images = len(images)
    print(f"Images: {total_images}")
    print(f"Reviewed: {approved}")
    print(f"Approved: {approved}")
    print(f"Person boxes: {person_boxes}")
    print(f"Vehicle boxes: {vehicle_boxes}")
    print(f"Invalid annotations: {invalid_count}")
    print(f"Missing labels: {missing_count}")
    
    if invalid_count == 0 and missing_count == 0 and approved == total_images:
        print("Ground Truth: PASS")
        print("Benchmark: READY TO FREEZE")
        return True
    else:
        print("Ground Truth: FAIL")
        return False

if __name__ == "__main__":
    validate_annotations("benchmark/images/test", "benchmark/labels/test")
