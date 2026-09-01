import os
import argparse
import json
import time
from pathlib import Path
import torch
import cv2
import numpy as np
import datetime
import subprocess

# Model Agnostic Evaluator for IBVAP
# Supports YOLOv11n and RF-DETR

# IBVAP Base Classes
IBVAP_CLASSES = {
    0: "person",
    1: "vehicle"
}

# RF-DETR to IBVAP Class Mapping
# RF-DETR uses COCO taxonomy. We map only relevant classes.
RFDETR_CLASS_MAPPING = {
    0: 0, # person -> person
    2: 1, # car -> vehicle
    3: 1, # motorcycle -> vehicle
    5: 1, # bus -> vehicle
    7: 1, # truck -> vehicle
}

def calculate_iou(boxA, boxB):
    # Determine the coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # Compute the area of intersection rectangle
    interArea = max(0, xB - xA) * max(0, yB - yA)

    # Compute the area of both bounding boxes
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou

class DetectorInterface:
    def load(self):
        pass
    def predict(self, image_path, conf_thresh):
        return []

class RFDETRDetector(DetectorInterface):
    def __init__(self, model_name='rfdetr-s', device='cpu'):
        self.model_name = model_name
        self.device = device
        self.model = None

    def load(self):
        try:
            from rfdetr import RFDETRSmall
            self.model = RFDETRSmall()
            # rfdetr manages device internally or via optimize_for_inference, but let's stick to CPU
        except ImportError:
            raise ImportError("rfdetr package not found. Run 'pip install rfdetr'")

    def predict(self, image_path, conf_thresh):
        results = self.model.predict(image_path, conf=conf_thresh)
        detections = []
        # Parse official RFDETR output (assuming format similar to ultralytics or dictionary)
        # We will handle a generic representation based on standard rfdetr wrapper
        for res in results:
            # Depending on rfdetr API, typically it provides boxes, labels, scores
            if hasattr(res, 'boxes'):
                boxes = res.boxes.xyxy.cpu().numpy()
                scores = res.boxes.conf.cpu().numpy()
                classes = res.boxes.cls.cpu().numpy().astype(int)
                for box, score, cls in zip(boxes, scores, classes):
                    if cls in RFDETR_CLASS_MAPPING:
                        ibvap_cls = RFDETR_CLASS_MAPPING[cls]
                        detections.append({
                            'class_id': ibvap_cls,
                            'class_name': IBVAP_CLASSES[ibvap_cls],
                            'confidence': float(score),
                            'x1': float(box[0]), 'y1': float(box[1]),
                            'x2': float(box[2]), 'y2': float(box[3])
                        })
        return detections

class YOLODetector(DetectorInterface):
    def __init__(self, model_name='yolo11n.pt', device='cpu'):
        self.model_name = model_name
        self.device = device
        self.model = None
        
    def load(self):
        from ultralytics import YOLO
        self.model = YOLO(self.model_name)
        
    def predict(self, image_path, conf_thresh):
        results = self.model(image_path, conf=conf_thresh, device=self.device, verbose=False)
        detections = []
        for res in results:
            boxes = res.boxes.xyxy.cpu().numpy()
            scores = res.boxes.conf.cpu().numpy()
            classes = res.boxes.cls.cpu().numpy().astype(int)
            for box, score, cls in zip(boxes, scores, classes):
                # YOLO11n trained on IBVAP directly outputs 0/1, or if COCO, map it
                # Assuming this yolo is the IBVAP baseline (0=person, 1=vehicle)
                # If COCO, we'd need mapping. We assume direct for now or map similar to RF-DETR
                mapped_cls = RFDETR_CLASS_MAPPING.get(cls, cls) if "11n" not in self.model_name else cls
                if mapped_cls in IBVAP_CLASSES:
                    detections.append({
                        'class_id': int(mapped_cls),
                        'class_name': IBVAP_CLASSES[int(mapped_cls)],
                        'confidence': float(score),
                        'x1': float(box[0]), 'y1': float(box[1]),
                        'x2': float(box[2]), 'y2': float(box[3])
                    })
        return detections

def load_ground_truth(label_path, img_width, img_height):
    gt = []
    if not os.path.exists(label_path):
        return gt
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                cls_id = int(parts[0])
                if cls_id not in IBVAP_CLASSES: continue
                cx = float(parts[1]) * img_width
                cy = float(parts[2]) * img_height
                w = float(parts[3]) * img_width
                h = float(parts[4]) * img_height
                gt.append({
                    'class_id': cls_id,
                    'x1': max(0, cx - w/2), 'y1': max(0, cy - h/2),
                    'x2': min(img_width, cx + w/2), 'y2': min(img_height, cy + h/2)
                })
    return gt

def draw_visual_report(image_path, gt_boxes, pred_boxes, matched_preds, matched_gts, out_path):
    img = cv2.imread(image_path)
    if img is None: return
    
    # Green = GT, Blue = TP, Red = FP, Orange = Missed (FN)
    for i, gt in enumerate(gt_boxes):
        if i not in matched_gts: # FN
            cv2.rectangle(img, (int(gt['x1']), int(gt['y1'])), (int(gt['x2']), int(gt['y2'])), (0, 165, 255), 2)
            cv2.putText(img, "FN", (int(gt['x1']), int(gt['y1'])-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
        else: # Matched GT -> Green
            cv2.rectangle(img, (int(gt['x1']), int(gt['y1'])), (int(gt['x2']), int(gt['y2'])), (0, 255, 0), 2)
            
    for i, pred in enumerate(pred_boxes):
        if i in matched_preds: # TP
            cv2.rectangle(img, (int(pred['x1']), int(pred['y1'])), (int(pred['x2']), int(pred['y2'])), (255, 0, 0), 2)
        else: # FP
            cv2.rectangle(img, (int(pred['x1']), int(pred['y1'])), (int(pred['x2']), int(pred['y2'])), (0, 0, 255), 2)
            cv2.putText(img, "FP", (int(pred['x1']), int(pred['y1'])-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
    cv2.imwrite(str(out_path), img)

def get_git_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    except:
        return "unknown"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='rfdetr-s', help='Model to evaluate: rfdetr-s or yolo11n')
    parser.add_argument('--conf', type=float, default=0.25, help='Confidence threshold')
    parser.add_argument('--iou', type=float, default=0.50, help='IoU threshold')
    parser.add_argument('--device', type=str, default='cpu', help='Device: cpu or cuda')
    parser.add_argument('--output', type=str, default='benchmark/results/rfdetr', help='Output dir')
    parser.add_argument('--save-visualizations', action='store_true', help='Save visual error reports')
    args = parser.parse_args()

    # Paths
    img_dir = Path("benchmark/images/test")
    lbl_dir = Path("benchmark/labels/test")
    out_dir = Path(args.output)
    
    if not img_dir.exists() or not lbl_dir.exists():
        print(f"ERROR: Benchmark directories do not exist! ({img_dir} or {lbl_dir})")
        print("Cannot run evaluation without frozen IBVAP-GT-v1.0.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    if args.save_visualizations:
        (out_dir / "visualizations").mkdir(parents=True, exist_ok=True)
        
    print(f"Loading model {args.model}...")
    if 'rfdetr' in args.model:
        detector = RFDETRDetector(args.model, args.device)
    else:
        detector = YOLODetector(args.model, args.device)
        
    detector.load()
    
    metrics = {
        'total_time': 0,
        'frames': 0,
        'TP': {0:0, 1:0},
        'FP': {0:0, 1:0},
        'FN': {0:0, 1:0}
    }
    
    frame_results = []
    
    for img_path in img_dir.glob("*.jpg"):
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        
        img = cv2.imread(str(img_path))
        h, w = img.shape[:2]
        
        gt_boxes = load_ground_truth(lbl_path, w, h)
        
        start_t = time.time()
        preds = detector.predict(str(img_path), args.conf)
        inf_time = time.time() - start_t
        metrics['total_time'] += inf_time
        metrics['frames'] += 1
        
        matched_preds = set()
        matched_gts = set()
        
        frame_tp = {0:0, 1:0}
        frame_fp = {0:0, 1:0}
        frame_fn = {0:0, 1:0}
        
        # Matching logic
        for cls_id in IBVAP_CLASSES:
            cls_preds = [p for p in preds if p['class_id'] == cls_id]
            cls_gts = [g for g in gt_boxes if g['class_id'] == cls_id]
            
            # Sort preds by confidence
            cls_preds = sorted(cls_preds, key=lambda x: x['confidence'], reverse=True)
            
            used_gts = set()
            for p_idx, p in enumerate(preds):
                if p['class_id'] != cls_id: continue
                
                best_iou = 0
                best_gt_idx = -1
                for g_idx, g in enumerate(gt_boxes):
                    if g['class_id'] != cls_id or g_idx in used_gts: continue
                    iou = calculate_iou([p['x1'],p['y1'],p['x2'],p['y2']], [g['x1'],g['y1'],g['x2'],g['y2']])
                    if iou > best_iou:
                        best_iou = iou
                        best_gt_idx = g_idx
                        
                if best_iou >= args.iou:
                    used_gts.add(best_gt_idx)
                    matched_preds.add(p_idx)
                    matched_gts.add(best_gt_idx)
                    frame_tp[cls_id] += 1
                    metrics['TP'][cls_id] += 1
                else:
                    frame_fp[cls_id] += 1
                    metrics['FP'][cls_id] += 1
            
            fn_count = len(cls_gts) - len(used_gts)
            frame_fn[cls_id] += fn_count
            metrics['FN'][cls_id] += fn_count
            
        frame_results.append({
            'image': img_path.name,
            'inference_time': inf_time,
            'TP': frame_tp,
            'FP': frame_fp,
            'FN': frame_fn
        })
        
        if args.save_visualizations and (sum(frame_fp.values()) > 0 or sum(frame_fn.values()) > 0):
            draw_visual_report(str(img_path), gt_boxes, preds, matched_preds, matched_gts, out_dir / "visualizations" / img_path.name)
            
    # Calculate aggregate metrics
    def calc_metrics(tp, fp, fn):
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        return p, r, f1
        
    p0, r0, f10 = calc_metrics(metrics['TP'][0], metrics['FP'][0], metrics['FN'][0])
    p1, r1, f11 = calc_metrics(metrics['TP'][1], metrics['FP'][1], metrics['FN'][1])
    
    # Save metadata
    run_meta = {
        'timestamp': datetime.datetime.now().isoformat(),
        'git_commit': get_git_commit(),
        'model': args.model,
        'conf_thresh': args.conf,
        'iou_thresh': args.iou,
        'frames_evaluated': metrics['frames'],
        'average_inference_time': metrics['total_time'] / max(1, metrics['frames']),
        'metrics': {
            'person': {'TP': metrics['TP'][0], 'FP': metrics['FP'][0], 'FN': metrics['FN'][0], 'Precision': p0, 'Recall': r0, 'F1': f10},
            'vehicle': {'TP': metrics['TP'][1], 'FP': metrics['FP'][1], 'FN': metrics['FN'][1], 'Precision': p1, 'Recall': r1, 'F1': f11},
        }
    }
    
    with open(out_dir / "run_metadata.json", "w") as f:
        json.dump(run_meta, f, indent=4)
        
    print("Evaluation completed successfully.")
    print(json.dumps(run_meta['metrics'], indent=2))

if __name__ == "__main__":
    main()
