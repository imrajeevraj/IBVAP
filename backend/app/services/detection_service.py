import torch
import cv2
import logging
import hashlib
import os
import threading
import time
from typing import List, Dict, Any, Tuple
import numpy as np
from ultralytics import YOLO

from backend.app.core.config import settings
from backend.app.services.border_rules_service import border_rules_service

logger = logging.getLogger("DetectionService")

class DetectionService:
    """
    Centralized, thread-safe high-performance RF-DETR / YOLO inference engine.
    Singleton architecture ensures weights are initialized ONCE in GPU memory.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, model_path: str | None = None, conf_threshold: float = 0.25):
        if getattr(self, '_initialized', False):
            return
        
        self.conf_threshold = conf_threshold
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.inference_lock = threading.Lock()
        
        # Per-class confidence thresholds
        self.class_thresholds = {
            "person": 0.25,
            "car": 0.30,
            "motorcycle": 0.30,
            "bus": 0.30,
            "truck": 0.30,
            "drone": 0.20,
            "weapon": 0.25,
            "knife": 0.25,
            "gun": 0.25,
            "backpack": 0.30,
            "suitcase": 0.30
        }

        try:
            candidate_paths = [
                model_path,
                settings.MODEL_PATH,
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../border_threat_yolo.pt")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../yolo11n.pt")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../yolov8n.pt")),
            ]
            
            selected_path = None
            for cp in candidate_paths:
                if cp and os.path.isfile(cp):
                    selected_path = os.path.abspath(cp)
                    break
                    
            if not selected_path:
                raise FileNotFoundError("No valid model weights found in configured paths.")

            logger.info("=" * 60)
            logger.info("INITIALIZING PERSISTENT DETECTION ENGINE")
            logger.info("=" * 60)
            logger.info(f"Loading verified model: {os.path.basename(selected_path)}")
            logger.info(f"Target Device: {self.device.upper()}")
            
            self.model = YOLO(selected_path)
            
            # Load specialized secondary model if it exists
            self.secondary_model = None
            if settings.SPECIALIZED_THREAT_MODEL_PATH:
                sec_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../", settings.SPECIALIZED_THREAT_MODEL_PATH))
                if os.path.isfile(sec_path):
                    logger.info(f"Loading specialized threat model: {settings.SPECIALIZED_THREAT_MODEL_PATH}")
                    self.secondary_model = YOLO(sec_path)
            
            if self.device.startswith("cuda"):
                torch.backends.cudnn.benchmark = True
                self.model.to(self.device)
                if hasattr(self.model, 'model') and self.model.model is not None:
                    self.model.model.half()
                gpu_name = torch.cuda.get_device_name(0)
                vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**2)
                logger.info(f"AI DEVICE: CUDA ({gpu_name})")
                logger.info(f"MODEL DEVICE: {self.device}")
                logger.info(f"INPUT DEVICE: {self.device}")
                logger.info(f"VRAM Capacity: {vram_total:.1f} MB (FP16 Tensor Cores Activated)")
                if self.secondary_model:
                    self.secondary_model.to(self.device)
                    if hasattr(self.secondary_model, 'model') and self.secondary_model.model is not None:
                        self.secondary_model.model.half()
            else:
                logger.info("AI DEVICE: CPU")
                logger.info("MODEL DEVICE: cpu")
                logger.info("INPUT DEVICE: cpu")

            # Warmup
            logger.info("Warming up inference engine...")
            dummy = np.zeros((640, 640, 3), dtype=np.uint8)
            with self.inference_lock:
                for _ in range(3):
                    _ = self.model.predict(source=dummy, imgsz=640, device=self.device, verbose=False)
                    if self.secondary_model:
                        _ = self.secondary_model.predict(source=dummy, imgsz=640, device=self.device, verbose=False)
            if self.device.startswith("cuda"):
                torch.cuda.synchronize()
            logger.info("Detection engine warmup complete.")

        except Exception as e:
            logger.error(f"Failed to load detection model: {e}")
            self.model = None

        # Desired classes mapping
        desired_classes = {
            "person", "car", "motorcycle", "bus", "truck", 
            "drone", "airplane", "backpack", "handbag", 
            "suitcase", "knife", "cell phone", "weapon", "gun"
        }

        self.target_classes = {}
        if self.model and hasattr(self.model, 'names'):
            for cls_id, cls_name in self.model.names.items():
                c_low = cls_name.lower()
                if c_low in desired_classes:
                    if c_low in ["airplane"]:
                        self.target_classes[cls_id] = "drone"
                    elif c_low in ["knife", "gun"]:
                        self.target_classes[cls_id] = "weapon"
                    else:
                        self.target_classes[cls_id] = c_low
            logger.info(f"Mapped {len(self.target_classes)} target classes: {list(self.target_classes.values())}")
        else:
            logger.warning("Could not read model.names, using default fallback classes.")

        self.colors = {
            "person": (0, 210, 235),     # Cyan
            "car": (56, 189, 248),       # Sky Blue
            "motorcycle": (56, 189, 248),# Sky Blue
            "bus": (245, 158, 11),       # Amber
            "truck": (245, 158, 11),     # Amber
            "drone": (239, 68, 68),      # Red
            "backpack": (168, 85, 247),  # Purple
            "handbag": (168, 85, 247),   # Purple
            "suitcase": (168, 85, 247),  # Purple
            "weapon": (239, 68, 68),     # Red
            "knife": (239, 68, 68),      # Red
            "gun": (239, 68, 68),        # Red
            "cell phone": (168, 85, 247) # Purple
        }
        self._initialized = True

    def predict_raw(self, frame: np.ndarray, imgsz: int = 640) -> Tuple[List[Dict[str, Any]], float]:
        """
        Execute isolated object detection forward pass with timing.
        Returns: (raw_detections, inference_latency_ms)
        """
        if self.model is None or frame is None:
            return [], 0.0

        t0 = time.perf_counter()
        with self.inference_lock:
            results = self.model.predict(
                source=frame,
                imgsz=imgsz,
                conf=self.conf_threshold,
                classes=list(self.target_classes.keys()) if self.target_classes else None,
                device=self.device,
                verbose=False
            )
            
            # Run secondary specialized model if available
            sec_results = []
            if self.secondary_model:
                sec_results = self.secondary_model.predict(
                    source=frame,
                    imgsz=imgsz,
                    conf=self.conf_threshold,
                    device=self.device,
                    verbose=False
                )
        if self.device.startswith("cuda"):
            torch.cuda.synchronize()
        latency_ms = (time.perf_counter() - t0) * 1000.0

        detections = []
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                label = self.target_classes.get(cls_id, self.model.names.get(cls_id, "unknown"))
                
                # Class-specific confidence filter
                min_conf = self.class_thresholds.get(label, self.conf_threshold)
                if conf < min_conf:
                    continue

                xyxy = [round(float(v), 1) for v in box.xyxy[0].tolist()]
                detections.append({
                    "class": label,
                    "confidence": round(conf, 2),
                    "box": xyxy,
                })
        
        # Merge specialized model detections
        if len(sec_results) > 0:
            result = sec_results[0]
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                label = self.secondary_model.names.get(cls_id, "unknown")
                
                # Default filter for secondary model
                if conf < self.conf_threshold:
                    continue
                
                xyxy = [round(float(v), 1) for v in box.xyxy[0].tolist()]
                detections.append({
                    "class": label,
                    "confidence": round(conf, 2),
                    "box": xyxy,
                })
        
        # Simple NMS: specialized classes override base classes on overlap
        final_detections = []
        specialized_classes = {"drone", "weapon", "contraband"}
        for det in detections:
            is_specialized = det["class"] in specialized_classes
            overlap = False
            
            # If it's a base class, check if it overlaps with any specialized detection
            if not is_specialized:
                for other in detections:
                    if other["class"] in specialized_classes:
                        # Check IoU
                        boxA = det["box"]
                        boxB = other["box"]
                        xA = max(boxA[0], boxB[0])
                        yA = max(boxA[1], boxB[1])
                        xB = min(boxA[2], boxB[2])
                        yB = min(boxA[3], boxB[3])
                        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
                        if interArea > 0:
                            boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
                            iou = interArea / float(boxAArea)
                            if iou > 0.5:
                                overlap = True
                                break
            
            if not overlap:
                final_detections.append(det)

        return final_detections, latency_ms

    def draw_detections(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """Render clean, anti-aliased tactical HUD bounding boxes."""
        for det in detections:
            box = det.get("box", [0, 0, 0, 0])
            x1, y1, x2, y2 = [int(v) for v in box]
            label = det.get("class", "object")
            conf = det.get("confidence", 0.0)
            color = self.colors.get(label, (0, 210, 235))
            track_id = det.get("track_id")

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Corner accents
            c_len = max(8, min(20, (x2 - x1) // 5))
            cv2.line(frame, (x1, y1), (x1 + c_len, y1), (255, 255, 255), 2)
            cv2.line(frame, (x1, y1), (x1, y1 + c_len), (255, 255, 255), 2)
            cv2.line(frame, (x2, y2), (x2 - c_len, y2), (255, 255, 255), 2)
            cv2.line(frame, (x2, y2), (x2, y2 - c_len), (255, 255, 255), 2)

            # Label text
            display_text = f"{label.upper()} {conf:.2f}"
            if track_id:
                clean_id = track_id.split(":")[-1]
                display_text = f"{clean_id} · {display_text}"

            (tw, th), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(frame, (x1, max(0, y1 - th - 6)), (x1 + tw + 6, y1), (13, 17, 23), -1)
            cv2.putText(frame, display_text, (x1 + 3, max(th + 2, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

        return frame

    def draw_zones(self, frame: np.ndarray, camera_id: str) -> np.ndarray:
        """Render security boundary zones and virtual tripwires."""
        config = border_rules_service.get_camera_config(camera_id)
        
        # Restricted Zones
        for zone in config.get("restricted_zones", []):
            poly = zone.get("polygon")
            if poly:
                pts = np.array(poly, np.int32).reshape((-1, 1, 2))
                overlay = frame.copy()
                cv2.fillPoly(overlay, [pts], (239, 68, 68))  # Red fill
                frame = cv2.addWeighted(overlay, 0.15, frame, 0.85, 0)
                cv2.polylines(frame, [pts], isClosed=True, color=(239, 68, 68), thickness=2)
                label = zone.get("name") or zone.get("id", "Restricted")
                x, y = pts[0][0]
                cv2.putText(frame, label, (int(x), max(24, int(y) - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (239, 68, 68), 1, cv2.LINE_AA)
                
        # Virtual Fences
        for fence in config.get("virtual_fences", []):
            line = fence.get("line")
            if line and len(line) == 2:
                p1 = tuple(map(int, line[0]))
                p2 = tuple(map(int, line[1]))
                cv2.line(frame, p1, p2, (0, 210, 235), thickness=2)  # Cyan tripwire
                label = fence.get("name") or fence.get("id", "Tripwire")
                midpoint = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
                cv2.putText(frame, label, (midpoint[0] + 6, max(24, midpoint[1] - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 210, 235), 1, cv2.LINE_AA)
                
        return frame

# Export singleton instance
detection_service = DetectionService()
