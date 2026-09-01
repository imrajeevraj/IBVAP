import os
import json
import glob

def validate_conversion(split_name, yolo_lbl_dir, coco_json_path):
    print(f"Validating {split_name} conversion...")
    
    with open(coco_json_path, "r") as f:
        coco = json.load(f)
        
    coco_img_count = len(coco["images"])
    coco_ann_count = len(coco["annotations"])
    
    # Count YOLO
    yolo_labels = glob.glob(f"{yolo_lbl_dir}/*.txt")
    yolo_ann_count = 0
    for lbl in yolo_labels:
        with open(lbl, "r") as f:
            for line in f:
                if line.startswith("#"): continue
                if len(line.strip().split()) == 5:
                    yolo_ann_count += 1
                    
    # The number of images should match the number of YOLO txt files 
    # (since our script copies all images even if no objects)
    yolo_img_count = len(glob.glob(f"{yolo_lbl_dir.replace('labels', 'images')}/*.jpg"))
    
    if coco_img_count != yolo_img_count:
        print(f"Mismatch in image count: YOLO {yolo_img_count} vs COCO {coco_img_count}")
        return False
        
    if coco_ann_count != yolo_ann_count:
        print(f"Mismatch in annotation count: YOLO {yolo_ann_count} vs COCO {coco_ann_count}")
        return False
        
    print(f"{split_name} Validation PASS: Images={coco_img_count}, Annotations={coco_ann_count}")
    return True

if __name__ == "__main__":
    v1 = validate_conversion("train", "benchmark/labels/train", "benchmark/rfdetr_dataset/train/_annotations.coco.json")
    v2 = validate_conversion("valid", "benchmark/labels/valid", "benchmark/rfdetr_dataset/valid/_annotations.coco.json")
    v3 = validate_conversion("test", "benchmark/labels/test", "benchmark/rfdetr_dataset/test/_annotations.coco.json")
    
    if v1 and v2 and v3:
        print("Dataset Conversion Validated Successfully.")
    else:
        print("Dataset Conversion Validation FAILED.")
