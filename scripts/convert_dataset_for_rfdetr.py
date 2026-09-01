import os
import json
import glob
import cv2
import shutil

def convert_yolo_to_coco(split_name, img_dir, lbl_dir, out_dir):
    print(f"Converting {split_name} to COCO format...")
    os.makedirs(out_dir, exist_ok=True)
    
    coco = {
        "images": [],
        "annotations": [],
        "categories": [
            {"id": 0, "name": "person", "supercategory": "none"},
            {"id": 1, "name": "vehicle", "supercategory": "none"}
        ]
    }
    
    ann_id = 0
    images = glob.glob(f"{img_dir}/*.jpg")
    for img_id, img_path in enumerate(images):
        basename = os.path.basename(img_path)
        name, _ = os.path.splitext(basename)
        
        # Copy image directly into the split folder
        shutil.copy(img_path, os.path.join(out_dir, basename))
        
        # Image info
        img = cv2.imread(img_path)
        h, w = img.shape[:2]
        coco["images"].append({
            "id": img_id,
            "file_name": basename,
            "width": w,
            "height": h
        })
        
        # Labels
        lbl_path = os.path.join(lbl_dir, f"{name}.txt")
        if os.path.exists(lbl_path):
            with open(lbl_path, "r") as f:
                for line in f:
                    if line.startswith("#"): continue
                    parts = line.strip().split()
                    if len(parts) != 5: continue
                    
                    cls_id = int(parts[0])
                    x_center, y_center, width, height = map(float, parts[1:])
                    
                    # YOLO to COCO
                    box_w = width * w
                    box_h = height * h
                    box_x = (x_center * w) - (box_w / 2)
                    box_y = (y_center * h) - (box_h / 2)
                    
                    coco["annotations"].append({
                        "id": ann_id,
                        "image_id": img_id,
                        "category_id": cls_id,
                        "bbox": [box_x, box_y, box_w, box_h],
                        "area": box_w * box_h,
                        "iscrowd": 0
                    })
                    ann_id += 1
                    
    with open(os.path.join(out_dir, "_annotations.coco.json"), "w") as f:
        json.dump(coco, f, indent=2)

if __name__ == "__main__":
    out_base = "benchmark/rfdetr_dataset"
    convert_yolo_to_coco("train", "benchmark/images/train", "benchmark/labels/train", os.path.join(out_base, "train"))
    convert_yolo_to_coco("valid", "benchmark/images/valid", "benchmark/labels/valid", os.path.join(out_base, "valid"))
    convert_yolo_to_coco("test", "benchmark/images/test", "benchmark/labels/test", os.path.join(out_base, "test"))
    print("Conversion complete.")
